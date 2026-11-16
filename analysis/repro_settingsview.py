"""Reproduce the triage's own 18/19 for SettingsView, using its own bodies() and its own pattern. (R810)

R809 applied the triage's declaration pattern to the raw file and got the complement of its result, which means one of
the two parts differed: the body or the pattern. This imports both from the module so neither can drift, and prints a
per-member verdict so the missing member is named rather than counted.
"""

import importlib.util
import re

TRIAGE = r"D:\projects\cyber-reverse\analysis\type_presence_triage.py"

spec = importlib.util.spec_from_file_location("triage", TRIAGE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

members = [m.strip() for m in mod.ABSENT["SettingsView"].split(",") if m.strip()]
bodies = mod.bodies()

print("  contract members: %d" % len(members))
print("  SettingsShell declarations collected: %d" % len(bodies.get("SettingsShell", [])))

hits = {}
for fn, body, doc in bodies.get("SettingsShell", []):
    print("    file=%s body=%d chars doc=%d chars" % (fn, len(body), len(doc)))
    for m in members:
        pat = re.compile(r"\b(?:public|internal)\s+[\w<>?\[\],. ]+\s+%s\s*(?:\{|=>|;|=)" % re.escape(m))
        if pat.search(body):
            hits[m] = fn

print()
print("  present: %d / %d" % (len(hits), len(members)))
missing = [m for m in members if m not in hits]
for m in missing:
    print("    MISSING: " + m)
print()
for m in members:
    print("    %-28s %s" % (m, hits.get(m, "-- absent --")))
