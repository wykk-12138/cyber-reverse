"""R659 step 1: snapshot every triage verdict BEFORE changing the scoring, so each change can be classified.

The change is to the member test: today the triage searches the class body for the member NAME anywhere; the fix is to
require a DECLARATION. That will move several verdicts, and without a before/after table a moved verdict looks like a
regression as easily as a correction. So the baseline is written first.
"""

import io
import json
import re
import sys

DOC = r"D:\projects\cyber-reverse\docs\TYPE_PRESENCE_TRIAGE.md"
OUT = r"D:\projects\cyber-reverse\analysis\triage_baseline.json"

ROW = re.compile(r"^\|\s*`(\w+)`\s*\|\s*\*\*([^|*]+?)\*\*\s*\|\s*(.*?)\s*\|\s*$")


def main():
    rows = []
    for line in io.open(DOC, encoding="utf-8").read().splitlines():
        m = ROW.match(line)
        if m:
            rows.append({"type": m.group(1), "verdict": m.group(2).strip(), "evidence": m.group(3).strip()})

    if len(rows) != 17:
        print("expected 17 rows, parsed %d -- refusing to write a baseline from a bad parse" % len(rows))
        return 1

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    print("baseline written: %s (%d rows)" % (OUT, len(rows)))
    for r in rows:
        print("  %-28s %s" % (r["type"], r["verdict"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
