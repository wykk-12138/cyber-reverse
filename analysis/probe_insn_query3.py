import io, json, subprocess, sys

analysis = r"C:\Users\wykk\AppData\Local\Cybersole\analysis"
args = analysis + r"\args_insn.json"

attempts = [
    {"queries": [{"mnem": "lea", "op_any": "146AAF344", "segment": ".text", "count": 20}]},
    {"queries": [{"mnem": "lea", "op_any": "146AAF344", "segment": "text", "count": 20}]},
    {"queries": [{"mnem": "lea", "op_any": "146AAF344", "start": "0x140001000",
                  "end": "0x147000000", "count": 20}]},
]

for a in attempts:
    io.open(args, "w", encoding="utf-8").write(json.dumps(a))
    out = subprocess.run([sys.executable, "ida_mcp.py", "call", "insn_query", "@" + args],
                         capture_output=True, text=True, cwd=analysis)
    text = (out.stdout or "") + (out.stderr or "")
    print("---", json.dumps(a)[:110])
    print(text.strip()[:600].replace("\n", " ")[:600])
    print()
