"""Talk to the IDA Pro MCP plugin over its HTTP JSON-RPC endpoint.

The plugin registers itself at http://127.0.0.1:<port>/mcp (GET returns 405, so it is POST-only).
This session has no mcp__ida__* tools, so the endpoint is called directly.

Usage:
    python ida_mcp.py list                 -> tool names + first line of each description
    python ida_mcp.py call <tool> [json]   -> call one tool
    python ida_mcp.py health               -> server_health

Kept deliberately small: it is a transport, not a wrapper. Every argument the plugin accepts is
passed through untouched so a wrong call fails in the plugin's own words rather than here.
"""
import io
import json
import sys
import urllib.request
import uuid

BASE = "http://127.0.0.1:13337/mcp"


def post(payload: dict, session: str | None = None) -> tuple[dict | None, str | None]:
    """POST one JSON-RPC message. Returns (parsed_body, session_id)."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    if session:
        req.add_header("Mcp-Session-Id", session)

    with urllib.request.urlopen(req, timeout=180) as resp:
        sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
        raw = resp.read().decode("utf-8", "replace")

    body = None
    if raw.strip():
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            # the endpoint may answer as an SSE stream: take the last data: line
            for line in reversed(raw.splitlines()):
                if line.startswith("data:"):
                    body = json.loads(line[5:].strip())
                    break
    return body, sid


def handshake() -> str | None:
    body, sid = post({
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "dsh-direct", "version": "1"},
        },
    })
    if body and "error" in body:
        print("initialize error:", json.dumps(body["error"])[:400], file=sys.stderr)
    return sid


def parse_result(body: dict | None):
    """MCP returns tools/call output as content blocks; JSON-ify when it is text."""
    if not body:
        return None
    if "error" in body:
        return {"error": body["error"]}
    result = body.get("result")
    if isinstance(result, dict) and isinstance(result.get("content"), list):
        parts = []
        for block in result["content"]:
            text = block.get("text") if isinstance(block, dict) else None
            if text is None:
                parts.append(block)
                continue
            try:
                parts.append(json.loads(text))
            except (json.JSONDecodeError, TypeError):
                parts.append(text)
        return parts[0] if len(parts) == 1 else parts
    return result


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    mode = sys.argv[1]
    sid = handshake()

    if mode == "list":
        body, _ = post({"jsonrpc": "2.0", "id": "2", "method": "tools/list", "params": {}}, sid)
        tools = (parse_result(body) or {}).get("tools", [])
        print(f"{len(tools)} tools\n")
        for t in tools:
            desc = (t.get("description") or "").strip().split("\n")[0][:96]
            print(f"  {t['name']:38} {desc}")
        return 0

    if mode == "health":
        body, _ = post({
            "jsonrpc": "2.0", "id": "3", "method": "tools/call",
            "params": {"name": "server_health", "arguments": {}},
        }, sid)
        print(json.dumps(parse_result(body), ensure_ascii=False, indent=2)[:2000])
        return 0

    if mode == "call":
        if len(sys.argv) < 3:
            print("need a tool name", file=sys.stderr)
            return 2
        name = sys.argv[2]

        # PowerShell 5.1 re-parses quotes when handing argv to a native exe, so inline JSON
        # arrives mangled. Prefer @file (one JSON object per file) and fall back to argv.
        if len(sys.argv) > 3 and sys.argv[3].startswith("@"):
            args = json.loads(io.open(sys.argv[3][1:], encoding="utf-8").read())
        elif len(sys.argv) > 3:
            args = json.loads(sys.argv[3])
        else:
            args = {}

        body, _ = post({
            "jsonrpc": "2.0", "id": "4", "method": "tools/call",
            "params": {"name": name, "arguments": args},
        }, sid)
        out = parse_result(body)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if mode == "py":
        # shorthand for py_eval: the whole argument is the Python source, read from a file so
        # quoting never crosses a shell boundary
        if len(sys.argv) < 3:
            print("need a .py file", file=sys.stderr)
            return 2
        src = io.open(sys.argv[2], encoding="utf-8").read()
        body, _ = post({
            "jsonrpc": "2.0", "id": "5", "method": "tools/call",
            "params": {"name": "py_eval", "arguments": {"code": src}},
        }, sid)
        out = parse_result(body)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print(f"unknown mode {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
