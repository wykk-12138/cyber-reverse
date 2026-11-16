"""Compare SettingsView's contract members with SettingsShell's, to name the missing one. (R809)"""

import io
import os
import re

TRIAGE_SCRIPT = r"D:\projects\cyber-reverse\analysis\type_presence_triage.py"
print("  === how the triage builds a contract ===")
t = io.open(TRIAGE_SCRIPT, encoding="utf-8", errors="replace").read()
for line in t.splitlines():
    s = line.strip()
    if re.search(r"def |members|contract|property|field|Getter|Setter", s) and len(s) < 120:
        print("    " + s[:112])

print()
POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
BINDS = r"D:\projects\cyber-reverse\docs\xaml_bindings.json"
print("  === SettingsView members from the pool / bindings ===")
seen = set()
if os.path.exists(BINDS):
    raw = io.open(BINDS, encoding="utf-8", errors="replace").read()
    print("    bindings file: %d chars" % len(raw))
    m = re.search(r'"SettingsView"\s*:\s*\[(.*?)\]', raw, re.S)
    if m:
        for name in re.findall(r'"([^"]+)"', m.group(1)):
            seen.add(name)
    print("    SettingsView binding entries: %d" % len(seen))
    for n in sorted(seen):
        print("      " + n)
else:
    print("    bindings file missing")
