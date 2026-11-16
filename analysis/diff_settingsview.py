"""Diff SettingsView's contract against SettingsShell's declarations to name the missing member. (R809)

The triage keeps its contracts in an ABSENT dict, so the nineteen member names are already written down. Import them
rather than retyping, then apply the same declaration pattern the triage uses, so the diff is measured the same way the
18/19 was.
"""

import io
import importlib.util
import os
import re

TRIAGE = r"D:\projects\cyber-reverse\analysis\type_presence_triage.py"
SHELL = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs"

spec = importlib.util.spec_from_file_location("triage", TRIAGE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

contract = [m.strip() for m in mod.ABSENT["SettingsView"].split(",") if m.strip()]
print("  SettingsView contract members: %d" % len(contract))

body = io.open(SHELL, encoding="utf-8", errors="replace").read()

present, missing = [], []
for m in contract:
    pat = re.compile(r"\b(?:public|internal)\s+[\w<>?\[\],. ]+\s+%s\s*(?:\{|=>|;|=)" % re.escape(m))
    (present if pat.search(body) else missing).append(m)

print("  declared in SettingsShell: %d" % len(present))
print("  missing:                   %d" % len(missing))
for m in missing:
    print("    " + m)

print()
print("  all contract members, with presence:")
for m in contract:
    print("    %-28s %s" % (m, "yes" if m in present else "NO"))
