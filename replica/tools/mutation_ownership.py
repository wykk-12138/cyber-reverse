"""Mutation test: with ownership in place, does R832's loose pattern still cross into another metric? (R834, take 2)

Take 1 read stdout for the summary table, which --skip-tests does not print -- it writes METRICS.md. Both row lists came
back empty and any() on an empty list is False, so the test reported PASS without measuring anything. This reads the
generated file instead, and fails when a row is missing rather than treating absence as cleanliness.

The mutation gives the functions metric the bare `replica:` pattern that caused the original bug, bound to a key it
legitimately owns. If ownership works that key appears in the functions row and never in the datafiles row. The real file
is restored in a finally block and METRICS.md is regenerated afterwards, because the mutation run overwrites it.
"""

import io
import subprocess
import sys

REPORT = r"tools\metrics_report.py"
GENERATED = r"..\docs\METRICS.md"

original = io.open(REPORT, encoding="utf-8").read()

mutated = original.replace(
    '"functions: replica .pdata", "functions: ratio"]),',
    '"functions: replica .pdata", "functions: ratio", "functions: LOOSE replica"]),',
    1)
step_one = mutated != original

mutated = mutated.replace(
    '        "functions: ratio": r"pdata-ratio:\\s*([\\d.]+%)",',
    '        "functions: ratio": r"pdata-ratio:\\s*([\\d.]+%)",\n'
    '        "functions: LOOSE replica": r"replica\\s*:\\s*([\\d,]+)",',
    1)
step_two = '"functions: LOOSE replica": r"replica' in mutated

if not step_one or not step_two:
    print("  MUTATION INCOMPLETE -- owned-list change: %s, pattern added: %s" % (step_one, step_two))
    print("  A half-applied mutation tests nothing, so this exits instead of reporting a result")
    sys.exit(1)

def rows(text, prefix):
    return [l.strip() for l in text.splitlines() if l.strip().startswith("| " + prefix)]

verdict = 0
io.open(REPORT, "w", encoding="utf-8", newline="").write(mutated)
print("  mutation applied: functions owns a bare 'replica:' pattern")
try:
    done = subprocess.run([sys.executable, REPORT, "--skip-tests"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if done.returncode != 0:
        print("  ! the mutated report failed to run: %s" % (done.stderr.strip()[:200]))
        sys.exit(1)
    written = io.open(GENERATED, encoding="utf-8", errors="replace").read()
    func_rows = rows(written, "函数数量")
    data_rows = rows(written, "数据文件名对照")

    if not func_rows or not data_rows:
        print("  ! rows missing from the generated file -- this proves nothing")
        print("    functions rows: %d, datafiles rows: %d" % (len(func_rows), len(data_rows)))
        verdict = 1
    else:
        print()
        for l in func_rows:
            print("    " + l[:112])
        print()
        for l in data_rows:
            print("    " + l[:112])
        print()
        claimed = any("LOOSE" in l for l in func_rows)
        crossed = any("LOOSE" in l for l in data_rows)
        print("  loose key appeared in the functions row : %s" % claimed)
        print("  loose key crossed into datafiles        : %s" % crossed)
        print()
        if crossed:
            print("  FAIL: ownership is decorative -- the loose pattern reached another metric")
            verdict = 1
        elif not claimed:
            print("  FAIL: the loose key did not even reach its own row, so the test is blind")
            verdict = 1
        else:
            print("  PASS: the loose pattern filled the row that owns it and no other")
finally:
    io.open(REPORT, "w", encoding="utf-8", newline="").write(original)
    subprocess.run([sys.executable, REPORT, "--skip-tests"], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
    print("  real file restored, METRICS.md regenerated")

sys.exit(verdict)
