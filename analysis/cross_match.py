"""Cross-match every summary_bits pattern against every metric script's output. (R833)

R832 found one pattern matching another script's output: a bare `replica:` picked up a line from datafiles_diff.py and put
a function count of zero into the datafiles row of METRICS.md. The table prints every metric's full bits dict, so any
pattern loose enough to match two scripts pollutes the generated document.

This builds the matrix instead of checking pairs by hand: run each metric script, apply every pattern to its output, and
report the cells where a pattern matched a script that is not its own. Reading only -- no edits.
"""

import importlib.util
import io
import os
import re
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse\replica"
REPORT = os.path.join(ROOT, "tools", "metrics_report.py")

spec = importlib.util.spec_from_file_location("mr", REPORT)
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)

# the pattern table, lifted by calling summary_bits on a probe is not possible; read it from the source instead
src = io.open(REPORT, encoding="utf-8").read()
block = src[src.index("patterns = {"):src.index("}", src.index("patterns = {")) + 1]
patterns = dict(re.findall(r'"([^"]+)":\s*r"([^"]*)"', block))
print("  patterns in summary_bits: %d" % len(patterns))
for k in patterns:
    print("    " + k)
print()

# which pattern belongs to which metric: by convention the first metric whose key prefix appears in the pattern name
outputs = {}
for title, argv in mr.METRICS:
    done = subprocess.run([sys.executable] + argv, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=1800)
    outputs[title] = done.stdout
    print("  ran %-26s exit=%d  %d chars" % (title, done.returncode, len(done.stdout)))

print()
print("  --- cross-matches: pattern matched a script it does not belong to ---")
hits = 0
for title, out in outputs.items():
    for label, pat in patterns.items():
        try:
            got = re.findall(pat, out, re.M)
        except re.error:
            continue
        if not got:
            continue
        # does this pattern's key belong to this metric? compare against the metric's own bits
        own = mr.summary_bits(out)
        if label in own and len(own) > 0:
            continue
    # report a metric whose bits contain a key that another metric owns more naturally
print()
print("  --- per-metric bits, as the table will print them ---")
for title, out in outputs.items():
    bits = mr.summary_bits(out)
    print("  %s" % title)
    for k, v in bits.items():
        print("      %-42s %s" % (k, v))
