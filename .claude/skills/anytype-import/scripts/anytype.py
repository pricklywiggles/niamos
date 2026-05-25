#!/usr/bin/env python3
"""Read-only Anytype API helper for piecemeal page-by-page migration.

Subcommands handle the deterministic IO parts of an import: talking to the local
Anytype REST API at http://127.0.0.1:31009, cleaning markdown, downloading icon
images, enumerating outgoing references. Decisions about *where* a page belongs
in the vault and whether to recurse into children stay with the calling agent.

Subcommands:
    fetch         SPACE_ID OBJECT_ID            JSON: cleaned page payload
    download-icon SPACE_ID OBJECT_ID --to DIR   download file-icon to DIR; print filename
                                                 (or emoji, or nothing if no icon)
    children      SPACE_ID OBJECT_ID            JSON: outgoing references to consider
    search        QUERY                         JSON: candidate pages across all spaces
    slug          NAME                          vault-safe filename (no extension)

All subcommands require ANYTYPE_API_KEY in the environment and a reachable
desktop API on port 31009. Network/auth/JSON errors exit with a one-line
"ERROR: ..." message — never a stack trace.
"""

import argparse
import http.client
import json
import os
import re
import socket
import sys
import urllib.parse
from pathlib import Path


API_HOST = "127.0.0.1"
API_PORT = 31009
API_VERSION = "2025-11-08"
DEFAULT_TIMEOUT = 10  # seconds; the desktop API is local so anything slower is a real problem


# --- HTTP layer ----------------------------------------------------------------

# Built on http.client rather than urllib.request because http.client takes
# host/port/path as separate arguments — no URL-scheme dispatch, so there's no
# way for a malicious or buggy URL to coerce a file:// or ftp:// read.

class HttpResponse:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body


def _http_request(method, host, port, path, *, headers=None, body=None, timeout=DEFAULT_TIMEOUT):
    """One-shot plaintext request over loopback. Returns HttpResponse or raises OSError-family.

    Encrypted transport is intentionally out of scope. Both endpoints we talk to
    (the Anytype REST API and the image gateway) listen on plain ports on 127.0.0.1,
    so the only thing on the wire is local IPC.
    """
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        return HttpResponse(resp.status, dict(resp.getheaders()), resp.read())
    finally:
        conn.close()


def _http_get(host, port, path, *, headers=None, timeout=DEFAULT_TIMEOUT):
    return _http_request("GET", host, port, path, headers=headers, timeout=timeout)


def _api_headers():
    key = os.environ.get("ANYTYPE_API_KEY", "").strip()
    if not key:
        sys.exit(
            "ERROR: ANYTYPE_API_KEY is not set. "
            "Add `export ANYTYPE_API_KEY=$(security find-generic-password -a anytype -s anytype-api -w)` "
            "to ~/.zshenv, then restart the shell."
        )
    return {
        "Authorization": f"Bearer {key}",
        "Anytype-Version": API_VERSION,
        "Accept": "application/json",
    }


def _api_call(method, path, params=None, body=None):
    if params:
        path = path + "?" + urllib.parse.urlencode(params)
    headers = _api_headers()
    body_bytes = None
    if body is not None:
        body_bytes = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        resp = _http_request(method, API_HOST, API_PORT, path, headers=headers, body=body_bytes)
    except (socket.timeout, ConnectionError, OSError) as e:
        sys.exit(
            f"ERROR: cannot reach Anytype API at {API_HOST}:{API_PORT} ({e}). "
            "Is the desktop app running and unlocked?"
        )

    if resp.status == 401:
        sys.exit("ERROR: 401 unauthorized — ANYTYPE_API_KEY is invalid or expired.")
    if resp.status == 404:
        sys.exit(f"ERROR: 404 not found at {path}. Object or space ID may be wrong.")
    if resp.status >= 400:
        snippet = resp.body[:200].decode("utf-8", errors="replace")
        sys.exit(f"ERROR: API returned HTTP {resp.status} for {path}: {snippet}")

    try:
        return json.loads(resp.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        sys.exit(f"ERROR: API returned non-JSON response for {path}: {e}")


def api_get(path, params=None):
    """GET an Anytype API path. Returns parsed JSON or exits with a user-facing error."""
    return _api_call("GET", path, params=params)


def api_post(path, body):
    """POST a JSON body to an Anytype API path. Same error semantics as api_get."""
    return _api_call("POST", path, body=body)


def _fetch_gateway_image(url):
    """Download an image from the Anytype gateway. Validates scheme + host.

    Gateway URLs look like http://127.0.0.1:47800/image/<hash>. We only allow
    loopback HTTP here — even though the API response is "trusted", a buggy or
    compromised desktop client could theoretically return any URL, and we don't
    want this script reaching off the box.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() != "http":
        sys.exit(f"ERROR: icon URL has non-http scheme: {parsed.scheme!r} (only http loopback is allowed).")
    if parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        sys.exit(f"ERROR: icon URL points off-host ({parsed.hostname!r}); refusing to fetch.")
    port = parsed.port or 80
    path = parsed.path + (("?" + parsed.query) if parsed.query else "")
    try:
        resp = _http_get(parsed.hostname, port, path)
    except (socket.timeout, ConnectionError, OSError) as e:
        sys.exit(f"ERROR: cannot fetch icon image from {url} ({e}).")
    if resp.status >= 400:
        sys.exit(f"ERROR: gateway returned HTTP {resp.status} for icon URL {url}.")
    return resp.body


# --- Markdown / body cleanup ---------------------------------------------------

# Whitespace characters Anytype emits inside leading indentation that look like
# ASCII spaces but aren't, so Markdown parsers don't recognize them as list
# nesting. We translate them to plain U+0020 only at line starts — preserving
# them in body text in case they're intentional typography.
_INDENT_WS_TRANSLATE = str.maketrans({
    " ": " ",  # NO-BREAK SPACE
    " ": " ",  # FIGURE SPACE (the one Anytype actually uses for bullets)
    " ": " ",  # THIN SPACE
    " ": " ",  # NARROW NO-BREAK SPACE
})


_INDENT_WS_CHARS = frozenset({" ", "\t", "\xa0", "\u2007", "\u2009", "\u202f"})


def _normalize_leading_indent(line):
    """Translate Unicode-space variants at the start of a line to ASCII spaces."""
    i = 0
    while i < len(line) and line[i] in _INDENT_WS_CHARS:
        i += 1
    return line[:i].translate(_INDENT_WS_TRANSLATE) + line[i:]


def clean_markdown(md):
    """Light cleanup; preserve structure and wording verbatim.

    Three transformations, all motivated by quirks of Anytype's serialization:

    1. Strip trailing whitespace per line. Anytype emits `   \\n` after nearly
       every line; Markdown treats 2+ trailing spaces as a hard line break,
       which makes rendered pages weirdly tall.
    2. Translate leading Unicode-space-variants (NBSP, figure space, etc.) to
       plain U+0020. Anytype uses U+2007 to indent nested bullets — Obsidian's
       Markdown parser won't recognize the nesting unless it's plain spaces.
    3. Collapse runs of 3+ blank lines down to 2.

    Capitalization, punctuation, code-fence languages, list markers — all
    preserved. Taste edits belong to the human, not the script.
    """
    if not md:
        return ""
    lines = [_normalize_leading_indent(line).rstrip() for line in md.splitlines()]
    out = []
    blank_run = 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run <= 2:
                out.append(line)
        else:
            blank_run = 0
            out.append(line)
    cleaned = "\n".join(out)
    if not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]*)?\]\]")


def extract_body_wikilinks(md):
    """Return ordered, deduped list of [[link]] targets in the body (no headings)."""
    seen = []
    for m in WIKILINK_RE.finditer(md or ""):
        target = m.group(1).strip()
        if target and target not in seen:
            seen.append(target)
    return seen


# --- Object inspection ---------------------------------------------------------

def _unwrap_object(payload):
    """API wraps single-object responses in `{object: {...}}`; lists in `{data: [...]}`."""
    if isinstance(payload, dict) and "object" in payload and isinstance(payload["object"], dict):
        return payload["object"]
    return payload


def _summarize_icon(icon):
    if not icon:
        return {"format": None, "value": None, "url": None}
    fmt = icon.get("format")
    if fmt == "emoji":
        return {"format": "emoji", "value": icon.get("emoji"), "url": None}
    if fmt == "file":
        return {"format": "file", "value": None, "url": icon.get("file")}
    # `format: "icon"` is the built-in icon set used by *types* (e.g. Page → document).
    # Pages themselves don't usually carry this, but surface it cleanly if they do.
    return {"format": fmt, "value": icon.get("name"), "url": None}


def _properties_summary(props):
    """Flatten the API's property array into a {key: simplified_value} dict."""
    summary = {}
    for p in props or []:
        key = p.get("key")
        fmt = p.get("format")
        if not key:
            continue
        if fmt == "date":
            summary[key] = p.get("date")
        elif fmt in ("multi_select", "select"):
            tags = p.get("multi_select") or p.get("select") or []
            summary[key] = [t.get("key") for t in tags if t.get("key")]
        elif fmt == "objects":
            summary[key] = p.get("objects") or []
        elif fmt == "text":
            summary[key] = p.get("text")
        elif fmt == "number":
            summary[key] = p.get("number")
        elif fmt == "checkbox":
            summary[key] = p.get("checkbox")
        elif fmt in ("url", "email", "phone"):
            summary[key] = p.get(fmt)
        else:
            summary[key] = p.get(fmt)  # best-effort for unknown formats
    return summary


# --- Subcommand: fetch ---------------------------------------------------------

def cmd_fetch(space_id, object_id):
    raw = api_get(f"/v1/spaces/{space_id}/objects/{object_id}", {"format": "md"})
    obj = _unwrap_object(raw)
    body = clean_markdown(obj.get("markdown") or "")
    out = {
        "id": obj.get("id"),
        "space_id": obj.get("space_id"),
        "title": obj.get("name"),
        "icon": _summarize_icon(obj.get("icon")),
        "type_key": (obj.get("type") or {}).get("key"),
        "type_name": (obj.get("type") or {}).get("name"),
        "layout": obj.get("layout"),
        "archived": obj.get("archived"),
        "snippet": obj.get("snippet"),
        "body_markdown": body,
        "body_length": len(body),
        "properties": _properties_summary(obj.get("properties")),
        "body_wikilinks": extract_body_wikilinks(body),
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# --- Subcommand: download-icon -------------------------------------------------

# Anytype gateway URLs look like http://127.0.0.1:47800/image/bafyrei...
# The hash has no extension and the API doesn't tell us the mime type. Sniff
# the magic bytes — covers the formats Anytype actually serves (PNG/JPEG/WebP/GIF).
_MAGIC_EXT = [
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"\xff\xd8\xff",       ".jpg"),
    (b"GIF87a",             ".gif"),
    (b"GIF89a",             ".gif"),
    (b"RIFF",               ".webp"),  # confirmed below by checking offset 8 for "WEBP"
    (b"<svg",               ".svg"),
    (b"<?xml",              ".svg"),
]


def _sniff_extension(blob, fallback=".png"):
    for sig, ext in _MAGIC_EXT:
        if blob.startswith(sig):
            if ext == ".webp" and not (len(blob) >= 12 and blob[8:12] == b"WEBP"):
                continue
            return ext
    return fallback


def cmd_download_icon(space_id, object_id, dest_dir, basename_hint=None):
    raw = api_get(f"/v1/spaces/{space_id}/objects/{object_id}")
    obj = _unwrap_object(raw)
    icon = _summarize_icon(obj.get("icon"))

    if icon["format"] is None:
        return  # no icon, nothing to print

    if icon["format"] == "emoji":
        # Caller decides where the emoji ends up (frontmatter value); just echo it.
        sys.stdout.write(icon["value"] or "")
        sys.stdout.write("\n")
        return

    if icon["format"] != "file" or not icon["url"]:
        sys.exit(f"ERROR: unsupported icon format {icon['format']!r}; cannot download.")

    dest = Path(dest_dir).expanduser()
    dest.mkdir(parents=True, exist_ok=True)

    blob = _fetch_gateway_image(icon["url"])

    ext = _sniff_extension(blob)
    # Use the page title (slugged) as the basename when possible — gateway hashes
    # are opaque and don't read well in the vault. Fall back to the URL hash.
    if basename_hint:
        base = basename_hint
    else:
        title = obj.get("name") or ""
        base = _slug(title) if title else Path(urllib.parse.urlparse(icon["url"]).path).name
    fname = f"{base}{ext}"
    out_path = dest / fname
    out_path.write_bytes(blob)
    sys.stdout.write(fname + "\n")


# --- Subcommand: children ------------------------------------------------------

def cmd_children(space_id, object_id):
    """Enumerate things the agent might want to follow from this page.

    Three sources:
      1. Outgoing relations of format `objects` (e.g. backlinks, links). We
         deliberately *exclude* "backlinks" — those are things pointing AT this
         page, not children of it.
      2. If the page is a collection or set, its members (via list-objects).
      3. [[Wikilink]] references parsed out of the body markdown. These are
         name-based, not ID-based, so the agent will need to resolve them later.

    Result is deduped by ID where possible, then by name for the body-only refs.
    """
    raw = api_get(f"/v1/spaces/{space_id}/objects/{object_id}", {"format": "md"})
    obj = _unwrap_object(raw)
    body = obj.get("markdown") or ""
    layout = obj.get("layout")

    candidates = []
    seen_ids = set()

    # 1. Object-valued properties (exclude backlinks — those point inward).
    for p in obj.get("properties") or []:
        if p.get("format") != "objects":
            continue
        key = p.get("key")
        if key in ("backlinks", "creator", "last_modified_by"):
            continue
        for oid in p.get("objects") or []:
            if oid in seen_ids or oid.startswith("_participant_"):
                continue
            seen_ids.add(oid)
            candidates.append({
                "id": oid,
                "name": None,
                "type": None,
                "source": "property",
                "hint": key,
            })

    # 2. Collection / set members. The 2025-11-08 API requires a two-step lookup:
    # GET /v1/spaces/<sid>/lists/<oid>/views to get the view IDs, then
    # GET /v1/spaces/<sid>/lists/<oid>/views/<view_id>/objects per view.
    # For sets the view's filters determine which objects come back, so we
    # iterate all views and dedupe — a collection usually has a single "All"
    # view that returns everything anyway.
    if layout in ("collection", "set"):
        views = api_get(f"/v1/spaces/{space_id}/lists/{object_id}/views", {"limit": 100})
        for v in views.get("data") or []:
            vid = v.get("id")
            if not vid:
                continue
            members = api_get(
                f"/v1/spaces/{space_id}/lists/{object_id}/views/{vid}/objects",
                {"limit": 1000},
            )
            for m in members.get("data") or []:
                mid = m.get("id")
                if not mid or mid in seen_ids:
                    continue
                seen_ids.add(mid)
                candidates.append({
                    "id": mid,
                    "name": m.get("name"),
                    "type": (m.get("type") or {}).get("key"),
                    "source": "collection",
                    "hint": layout,
                })

    # 3. Body wikilinks — name-based, can't resolve to IDs without another lookup.
    for name in extract_body_wikilinks(body):
        candidates.append({
            "id": None,
            "name": name,
            "type": None,
            "source": "body-link",
            "hint": None,
        })

    # Hydrate names for property-sourced IDs by hitting the object endpoint per ID.
    # Keep this best-effort: a failure to resolve one shouldn't kill the whole call.
    for c in candidates:
        if c["source"] == "property" and c["id"]:
            try:
                child_raw = api_get(f"/v1/spaces/{space_id}/objects/{c['id']}")
                child = _unwrap_object(child_raw)
                c["name"] = child.get("name")
                c["type"] = (child.get("type") or {}).get("key")
            except SystemExit:
                # Don't bail the whole listing if one child 404s; leave name as None.
                pass

    json.dump(candidates, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# --- Subcommand: plan ----------------------------------------------------------

# How many candidate IDs we'll resolve, total, across the whole walk. A hard
# cap prevents runaway recursion if someone points us at a hub object that's
# transitively linked to thousands of pages.
PLAN_MAX_PAGES = 500


def _collect_children_for_plan(space_id, object_id, sources):
    """Lighter version of cmd_children used by the recursive walker.

    Returns a list of {id, name, type, source} dicts (no body-link name-only
    entries unless requested). Different from cmd_children only in:
      - returns Python objects, not stdout JSON
      - filters by allowed sources
      - body-link entries are dropped if "body-link" not in sources, because
        they can't be followed without a name→id lookup
    """
    raw = api_get(f"/v1/spaces/{space_id}/objects/{object_id}", {"format": "md"})
    obj = _unwrap_object(raw)
    body = obj.get("markdown") or ""
    layout = obj.get("layout")

    found = []
    seen = set()

    if "property" in sources:
        for p in obj.get("properties") or []:
            if p.get("format") != "objects":
                continue
            if p.get("key") in ("backlinks", "creator", "last_modified_by"):
                continue
            for oid in p.get("objects") or []:
                if oid in seen or oid.startswith("_participant_"):
                    continue
                seen.add(oid)
                found.append({"id": oid, "name": None, "type": None, "source": "property"})

    if "collection" in sources and layout in ("collection", "set"):
        views = api_get(f"/v1/spaces/{space_id}/lists/{object_id}/views", {"limit": 100})
        for v in views.get("data") or []:
            vid = v.get("id")
            if not vid:
                continue
            members = api_get(
                f"/v1/spaces/{space_id}/lists/{object_id}/views/{vid}/objects",
                {"limit": 1000},
            )
            for m in members.get("data") or []:
                mid = m.get("id")
                if not mid or mid in seen:
                    continue
                seen.add(mid)
                found.append({
                    "id": mid,
                    "name": m.get("name"),
                    "type": (m.get("type") or {}).get("key"),
                    "source": "collection",
                })

    # body-link entries are name-only; we can't follow them blindly in the plan
    # because they need a search to resolve. Skip them for the recursive walk
    # but the agent can still surface them from the cmd_children output.

    return found


def cmd_plan(space_id, object_id, max_depth=5, sources=("collection",)):
    """Build the full set of pages reachable from object_id, breadth-first.

    Output JSON: list of {id, name, type, depth, parent_id, source}. The first
    entry is the root (depth=0). Order is BFS, so close-by pages come before
    far-away ones — useful for the agent to slice "import the first N" if the
    user wants to limit scope.

    Cycle-safe (dedupes by ID). Capped at PLAN_MAX_PAGES.
    """
    plan = []
    seen = set()
    # (parent_id, child_id, child_name_hint, child_type_hint, source)
    queue = [(None, object_id, None, None, "root", 0)]

    while queue and len(plan) < PLAN_MAX_PAGES:
        parent_id, oid, name_hint, type_hint, source, depth = queue.pop(0)
        if oid in seen:
            continue
        seen.add(oid)

        # Resolve the page so we know its name and whether to recurse.
        try:
            raw = api_get(f"/v1/spaces/{space_id}/objects/{oid}")
        except SystemExit:
            # Skip unresolvable IDs (e.g. cross-space links we don't have access to)
            # rather than aborting the whole plan.
            plan.append({
                "id": oid, "name": name_hint, "type": type_hint,
                "depth": depth, "parent_id": parent_id, "source": source,
                "error": "could not resolve",
            })
            continue
        obj = _unwrap_object(raw)
        plan.append({
            "id": oid,
            "name": obj.get("name") or name_hint,
            "type": (obj.get("type") or {}).get("key") or type_hint,
            "layout": obj.get("layout"),
            "depth": depth,
            "parent_id": parent_id,
            "source": source,
            "tag_keys": [
                t.get("key") for p in (obj.get("properties") or [])
                if p.get("key") == "tag" and p.get("multi_select")
                for t in p["multi_select"] if t.get("key")
            ],
        })

        if depth >= max_depth:
            continue

        try:
            kids = _collect_children_for_plan(space_id, oid, sources)
        except SystemExit:
            continue
        for k in kids:
            if k["id"] in seen:
                continue
            queue.append((oid, k["id"], k["name"], k["type"], k["source"], depth + 1))

    out = {
        "root": object_id,
        "total": len(plan),
        "capped": len(plan) >= PLAN_MAX_PAGES,
        "max_depth": max_depth,
        "sources": list(sources),
        "pages": plan,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# --- Subcommand: search --------------------------------------------------------

def cmd_search(query):
    # Search is POST with a JSON body, not GET — verified against API 2025-11-08.
    payload = api_post("/v1/search?limit=50", {"query": query})
    results = []
    for o in payload.get("data") or []:
        icon = _summarize_icon(o.get("icon"))
        tags = []
        for p in o.get("properties") or []:
            if p.get("key") == "tag" and p.get("multi_select"):
                tags = [t.get("key") for t in p["multi_select"] if t.get("key")]
        results.append({
            "id": o.get("id"),
            "name": o.get("name"),
            "space_id": o.get("space_id"),
            "snippet": (o.get("snippet") or "")[:200],
            "layout": o.get("layout"),
            "type": (o.get("type") or {}).get("key"),
            "has_icon": icon["format"] is not None,
            "tag_keys": tags,
        })
    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# --- Subcommand: slug ----------------------------------------------------------

# Forbidden in vault filenames: path separators and control chars. Everything
# else — including spaces, parens, ampersands, apostrophes — Obsidian handles
# fine, and we want filenames to match the original page title as closely as
# possible so wikilinks resolve naturally.
_FORBIDDEN_RE = re.compile(r"[\x00-\x1f/\\]")


def _slug(name):
    if not name:
        return "untitled"
    # Replace path separators with dashes; strip control chars.
    cleaned = _FORBIDDEN_RE.sub(lambda m: "-" if m.group() in ("/", "\\") else "", name)
    # Collapse whitespace runs to single spaces and strip ends.
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Strip trailing dots/spaces (macOS/Windows hostility).
    cleaned = cleaned.rstrip(". ")
    return cleaned or "untitled"


def cmd_slug(name):
    sys.stdout.write(_slug(name) + "\n")


# --- Entrypoint ----------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="Get a page's cleaned payload as JSON")
    p_fetch.add_argument("space_id")
    p_fetch.add_argument("object_id")

    p_icon = sub.add_parser("download-icon", help="Download a file-icon or echo the emoji")
    p_icon.add_argument("space_id")
    p_icon.add_argument("object_id")
    p_icon.add_argument("--to", required=True, help="Destination directory")
    p_icon.add_argument("--basename", help="Override the saved filename's basename (no extension)")

    p_children = sub.add_parser("children", help="Enumerate outgoing references")
    p_children.add_argument("space_id")
    p_children.add_argument("object_id")

    p_plan = sub.add_parser("plan", help="Recursively enumerate all pages reachable from a root")
    p_plan.add_argument("space_id")
    p_plan.add_argument("object_id")
    p_plan.add_argument("--max-depth", type=int, default=5, help="How deep to walk (default 5)")
    p_plan.add_argument(
        "--include-sources", default="collection",
        help="Comma-sep child sources to follow: collection,property (default: collection)",
    )

    p_search = sub.add_parser("search", help="Search globally by name/content")
    p_search.add_argument("query")

    p_slug = sub.add_parser("slug", help="Convert a page name to a vault-safe filename")
    p_slug.add_argument("name")

    args = parser.parse_args()

    if args.cmd == "fetch":
        cmd_fetch(args.space_id, args.object_id)
    elif args.cmd == "download-icon":
        cmd_download_icon(args.space_id, args.object_id, args.to, args.basename)
    elif args.cmd == "children":
        cmd_children(args.space_id, args.object_id)
    elif args.cmd == "plan":
        sources = tuple(s.strip() for s in args.include_sources.split(",") if s.strip())
        cmd_plan(args.space_id, args.object_id, max_depth=args.max_depth, sources=sources)
    elif args.cmd == "search":
        cmd_search(args.query)
    elif args.cmd == "slug":
        cmd_slug(args.name)


if __name__ == "__main__":
    main()
