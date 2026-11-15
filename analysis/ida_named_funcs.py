"""Ask IDA how many functions carry a real `Cybersole_*` name — the crux of blocker A (R570).

Why this is not covered by the existing tooling:

* `analysis/ida.py funcs <name>` calls `func_query` with `{'queries': [{'name_contains': …}]}`, and the plugin
  ignores that filter — it returned all 50 `sub_*` rows unchanged for both `CreateInputModel` and `Cybersole_`.
  So the wrapper as written cannot answer "which functions have real names".
* `analysis/ida.py tools` prints tool names and the first line of each description, not the input schemas, so the
  correct filter key cannot be read off it.
* The public repos (`seep-reverse-lab`, `rea`) cover the *method* (string → xrefs → function → Hex-Rays) but not
  this specific "does the image retain any managed symbol names" question.

So this prints the schema of `func_query` and then tries the plausible filter shapes, reporting which one actually
filters. Everything it prints is raw tool output; nothing is inferred.

Run with IDA open on `target/Cybersole.exe.i64`.
"""

import io
import json
import sys
import urllib.request

URL = "http://127.0.0.1:13337/mcp"
_id = [0]


def _rpc(method, params=None, timeout=300):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def call(tool, args=None):
    res = _rpc("tools/call", {"name": tool, "arguments": args or {}})
    if "error" in res:
        return "ERROR: " + json.dumps(res["error"], ensure_ascii=False)
    out = res.get("result", {})
    texts = [c.get("text", "") for c in (out.get("content") or []) if isinstance(c, dict)]
    return "\n".join(texts) if texts else json.dumps(out, ensure_ascii=False)


def schema_for(tool):
    tools = _rpc("tools/list", {}).get("result", {}).get("tools", [])
    for t in tools:
        if t.get("name") == tool:
            return t.get("inputSchema")
    return None


def main():
    _rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                        "clientInfo": {"name": "cyber-reverse", "version": "1"}})

    print("=== func_query inputSchema ===")
    sch = schema_for("func_query")
    print(json.dumps(sch, ensure_ascii=False, indent=1)[:1800] if sch else "(not found)")

    print()
    print("=== filter shapes tried ===")
    shapes = [
        # CONTROL: `__CxxQueryExceptionSize` is known to exist at 0x140001739 (it decompiled in this session),
        # so `^__` MUST return at least one row. If it returns 0, the query is broken and every other 0 below is
        # meaningless.
        ("CONTROL ^__", {"queries": [{"name_regex": "^__", "count": 5}]}),
        ("^Cybersole_", {"queries": [{"name_regex": "^Cybersole_", "count": 5}]}),
        ("^Cybersole", {"queries": [{"name_regex": "^Cybersole", "count": 5}]}),
        ("glob Cybersole_*", {"queries": [{"filter": "Cybersole_*", "count": 5}]}),
        ("^sub_ (page)", {"queries": [{"name_regex": "^sub_", "count": 5}]}),
    ]
    for label, args in shapes:
        try:
            raw = call("func_query", args)
        except Exception as exc:                     # noqa: BLE001 - report, do not crash
            print("  %-26s EXC %s" % (label, exc))
            continue
        try:
            parsed = json.loads(raw)
        except Exception:                            # noqa: BLE001
            print("  %-26s non-json: %s" % (label, raw[:120].replace("\n", " ")))
            continue

        # the plugin wraps results as [{"data": [...], "next_offset": N}]
        rows = parsed if isinstance(parsed, list) else [parsed]
        flat = []
        for item in rows:
            if isinstance(item, dict) and isinstance(item.get("data"), list):
                flat.extend(item["data"])
            elif isinstance(item, dict) and "name" in item:
                flat.append(item)
        names = [r.get("name", "") for r in flat if isinstance(r, dict)]
        real = [n for n in names if n and not n.startswith("sub_")]
        print("  %-26s rows=%-4d real-named=%-4d first=%s"
              % (label, len(names), len(real), (names[0] if names else "-")))


if __name__ == "__main__":
    sys.exit(main())
