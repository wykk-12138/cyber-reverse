import io, json, subprocess, sys, re

analysis = r"C:\Users\wykk\AppData\Local\Cybersole\analysis"
args = io.path.join(analysis, "args_ua.json") if hasattr(io, "path") else analysis + r"\args_ua.json"

io.open(args, "w", encoding="utf-8").write(json.dumps({"pattern": "Mozilla/5.0", "limit": 400}))

out = subprocess.run([sys.executable, "ida_mcp.py", "call", "find_regex", "@" + args],
                     capture_output=True, text=True, cwd=analysis)
text = (out.stdout or "") + (out.stderr or "")

io.open(analysis + r"\ua_raw.txt", "w", encoding="utf-8", newline="").write(text)

try:
    data = json.loads(out.stdout)
    if isinstance(data, list):
        data = data[0]
    print("n =", data.get("n"), " done =", (data.get("cursor") or {}).get("done"))
    print("truncated hint:", "output/" in text)
except Exception as ex:
    print("parse failed:", ex)
    print("head:", text[:300])
