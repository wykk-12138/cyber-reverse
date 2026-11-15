import io, json, subprocess, sys

analysis = r"C:\Users\wykk\AppData\Local\Cybersole\analysis"
args = analysis + r"\args_insn.json"

attempts = [
    {"queries": [{"mnemonic": "lea", "operand_contains": "6aaf344"}], "limit": 10},
    {"queries": [{"mnemonic": "lea"}], "limit": 3},
    {"mnemonic": "lea", "limit": 3},
]

for a in attempts:
    io.open(args, "w", encoding="utf-8").write(json.dumps(a))
    out = subprocess.run([sys.executable, "ida_mcp.py", "call", "insn_query", "@" + args],
                         capture_output=True, text=True, cwd=analysis)
    text = (out.stdout or "") + (out.stderr or "")
    print("---", json.dumps(a)[:80])
    print(text.strip()[:400].replace("\n", " ")[:400])
