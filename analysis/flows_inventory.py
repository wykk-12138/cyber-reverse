"""Enumerate the original's flow identifiers from the reflection metadata and compare with the replica's files.

Written as a file rather than an inline heredoc because the shell mangles quoting, and because the comparison is worth
re-running. Uses ida.py's --limit so the forty-match cap of R1024 does not apply.
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse"
FLOWS_DIR = os.path.join(ROOT, "replica", "src", "Cybersole.Stores", "Flows")

p = subprocess.run(
    [sys.executable, "analysis/ida.py", "str", r"Stores\.Flows\.[A-Za-z0-9_]+", "--limit", "600"],
    cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")

raw = p.stdout.strip()
if not raw:
    print("  no output; stderr:", p.stderr[:300])
    sys.exit(1)

try:
    data = json.loads(raw)
except Exception:
    # ida.py prints the MCP text block, which may be wrapped; find the outermost object.
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        print("  unparseable. head:", raw[:300])
        sys.exit(1)
    data = json.loads(m.group(0))

total = data.get("n")
names = set()
for hit in data.get("matches", []):
    for name in re.findall(r"Stores\.Flows\.([A-Za-z0-9_]+)", hit.get("string", "")):
        names.add(name)

print("  matches reported: %s   distinct identifiers: %d" % (total, len(names)))

# The original's flow-shaped identifiers, and which of them the replica has a file or type for.
flows = sorted(n for n in names if "Flow" in n)
print("\n  original flow-shaped identifiers: %d" % len(flows))
for name in flows:
    print("    " + name)

replica_files = sorted(
    f[:-3] for f in os.listdir(FLOWS_DIR) if f.endswith(".cs"))
print("\n  replica flow files: %d" % len(replica_files))

missing = []
for name in flows:
    stem = name[:-4] if name.endswith("Flow") else name
    if not any(stem.lower() in f.lower() for f in replica_files):
        missing.append(name)
print("  flow identifiers with no obviously matching replica file: %d" % len(missing))
for name in missing:
    print("    " + name)
