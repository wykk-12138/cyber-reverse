"""Wait until the IDA database is ready for string queries.

R94: the MCP plugin answers `/mcp` as soon as IDA has *started* loading, but `find_regex` builds a
strings cache over the whole image and dies with

    ida_mcp.sync.IDASyncError: Tool timed out after 60.00s

while auto-analysis is still running. So "the port is open" does not mean "queries work" — the
signal is `auto_analysis_ready` in `server_health`.

Usage:
    python ida_wait.py [max_minutes]     -> polls every 30 s, exits 0 when ready
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ida_mcp


def health():
    body, _ = ida_mcp.post({
        "jsonrpc": "2.0", "id": "1", "method": "tools/call",
        "params": {"name": "server_health", "arguments": {}},
    })
    text = json.dumps(body)
    return body, text


def main() -> int:
    limit = float(sys.argv[1]) if len(sys.argv) > 1 else 180.0
    deadline = time.time() + limit * 60

    while time.time() < deadline:
        try:
            body, text = health()
            result = body.get("result") or {}
            content = result.get("content") or []
            payload = {}
            if content and isinstance(content[0], dict) and content[0].get("text"):
                payload = json.loads(content[0]["text"])
            ready = payload.get("auto_analysis_ready")
            strings = payload.get("strings_cache_ready")
            print("auto_analysis_ready=%s strings_cache_ready=%s uptime=%ss" % (
                ready, strings, round(payload.get("uptime_sec", 0))))
            if ready:
                print("READY")
                return 0
        except Exception as ex:              # plugin not up yet, or restarting
            print("not up:", type(ex).__name__)

        time.sleep(30)

    print("TIMEOUT after %s minutes" % limit)
    return 1


if __name__ == "__main__":
    sys.exit(main())
