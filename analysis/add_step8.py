import io

p = r"D:\projects\cyber-reverse\replica\tools\verify-steps.ps1"
t = io.open(p, encoding="utf-8").read()

old = """    @{ N = 7; Name = 'mutation guards';      Run = { & 'D:\\projects\\IDA-pro\\python311\\python.exe' .\\tools\\mutation-check.py 2>&1 | Out-String } }"""

new = """    @{ N = 7; Name = 'mutation guards';      Run = { & 'D:\\projects\\IDA-pro\\python311\\python.exe' .\\tools\\mutation-check.py 2>&1 | Out-String } },
    # R128: every endpoint literal must appear verbatim in the string pool. This is the gate that
    # would have caught the Scheels /v5/Order/ invention twelve rounds before it was noticed.
    @{ N = 8; Name = 'endpoint provenance';  Run = { & 'D:\\projects\\IDA-pro\\python311\\python.exe' .\\tools\\endpoint-provenance.py 2>&1 | Out-String } }"""

if old not in t:
    raise SystemExit("step 7 anchor missing")
t = t.replace(old, new, 1)

# the docs step lists which docs must exist; nothing to add there.

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("step 8 added: endpoint provenance")
