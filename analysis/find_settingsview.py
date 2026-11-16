"""Find the one member that keeps SettingsView from matching SettingsShell. (R809)

The triage records SettingsView as STRUCTURAL: 18 of 19 member names co-occur in SettingsShell, and only one class
reaches that coverage. One member short is close enough to be worth resolving rather than leaving as unknown.
"""

import io
import re

TRIAGE = r"D:\projects\cyber-reverse\docs\TYPE_PRESENCE_TRIAGE.md"
t = io.open(TRIAGE, encoding="utf-8", errors="replace").read()
for line in t.splitlines():
    if "SettingsView" in line:
        print("  triage row:")
        print("    " + line[:200])

print()
print("  locating SettingsShell in the replica:")
import os
ROOT = r"D:\projects\cyber-reverse\replica\src"
for base, _d, files in os.walk(ROOT):
    if os.sep + "obj" in base or os.sep + "bin" in base:
        continue
    for f in files:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(base, f)
        src = io.open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"class\s+(SettingsShell|SettingsView)\b", src):
            print("    %s : %s" % (os.path.relpath(p, ROOT), m.group(1)))
