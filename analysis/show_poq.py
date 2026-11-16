"""Show which steps poq-app has and which it lacks, plus the evidence already gathered for it. (R805)"""

import io
import re

PATH = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\PoqAppFlow.cs"

t = io.open(PATH, encoding="utf-8", errors="replace").read()
print("  PoqAppFlow: %d lines" % len(t.splitlines()))
print()
print("  overrides:")
for line in t.splitlines():
    if re.search(r'override\s+(async\s+)?Task<StepOutcome>|override\s+bool', line):
        print("    " + line.strip()[:100])
print()
print("  endpoints / constants mentioned:")
for line in t.splitlines():
    s = line.strip()
    if re.search(r'(const string|"/|https://)', s) and not s.startswith("//"):
        print("    " + s[:104])
