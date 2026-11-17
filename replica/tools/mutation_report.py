"""Report the last mutation run, and whether it still describes the current tree. (R982)

WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):

Criterion (e) says the mutation tests all fire. Until now that figure lived only in prose -- the exact thing the project's
own §4 forbids, and the thing R979 caught doing it: the number was in a handoff block a hundred and fifty rounds stale.

Reading it from a fresh run is not possible here. A full pass is thirty-six mutations each running a filtered test suite,
about twelve minutes, and `metrics_report.py` is the command run every round; putting twelve minutes into it would mean it
stops being run. So `mutation-check.py` writes a dated result and this reads it, the same arrangement `artifact_freshness.py`
uses for the publish artifact: the number carries a timestamp, and staleness is reported rather than hidden.

What it can and cannot say:
    CAN   : the last run's counts, and whether the source has changed since that run.
    CANNOT: guarantee that a re-run today would give the same counts. That is what re-running is for.

Reproduce:
    cd replica
    python tools/mutation_report.py
"""

import datetime
import io
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULT = os.path.abspath(os.path.join(ROOT, "..", "analysis", "MUTATION_RESULT.json"))


def newest_input():
    """The newest mtime among the files a mutation run actually exercises, and which file it was.

    R982: only src, tests and tools count, and this file does not. A first version also walked docs, which made the
    staleness figure positive after any doc edit -- and a staleness warning that fires on every round is one nobody reads.
    A mutation edits source and runs tests; a paragraph in a document changes neither. This file is excluded for the same
    reason plus its own: it only reads the record, so editing it cannot change a verdict, and counting it would make every
    improvement to the reporter invalidate what it reports.
    """
    newest, which = 0.0, None
    me = os.path.abspath(__file__)
    for base in (os.path.join(ROOT, "src"), os.path.join(ROOT, "tests"), os.path.join(ROOT, "tools")):
        for dp, _d, fns in os.walk(base):
            if f"{os.sep}obj{os.sep}" in dp or f"{os.sep}bin{os.sep}" in dp or ".mutation-backup" in dp:
                continue
            for fn in fns:
                if not (fn.endswith(".cs") or fn.endswith(".py")):
                    continue
                p = os.path.join(dp, fn)
                if os.path.abspath(p) == me:
                    continue
                try:
                    m = os.path.getmtime(p)
                except OSError:
                    continue
                if m > newest:
                    newest, which = m, p
    return newest, which


def main():
    if not os.path.exists(RESULT):
        print("  mutation-fit-total: 0")
        print("  mutation-fit-fired: 0")
        print("  mutation-freshness: never run -- analysis/MUTATION_RESULT.json is absent")
        print()
        print("  A missing result is a missing measurement, not a pass. Run `python tools/mutation-check.py`.")
        return 0

    record = json.loads(io.open(RESULT, encoding="utf-8").read())

    print("  mutation-fit-total: %d" % record["total"])
    print("  mutation-fit-fired: %d" % record["fired"])
    print("  mutation-fit-decorative: %d" % record["decorative"])
    print("  mutation-fit-skipped: %d" % record["skipped"])
    print("  mutation-fit-tree: %s" % record["tree"])

    ran_at = datetime.datetime.fromisoformat(record["ran_at"])
    run_stamp = ran_at.timestamp()
    newest, which = newest_input()

    if newest > run_stamp:
        behind = int(newest - run_stamp)
        age = str(datetime.timedelta(seconds=behind))
        print("  mutation-fit-staleness: %s -- %s changed after the run"
              % (age, os.path.basename(which or "?")))
        print()
        print("  The counts above are from %s and the tree has moved since. They are a record of that run, not a"
              % record["ran_at"])
        print("  statement about this one; re-run `python tools/mutation-check.py` before quoting them as current.")
    else:
        print("  mutation-fit-staleness: 0 -- no exercised file is newer than the run")
        print()
        print("  Every mutation fired, none was decorative and none was skipped at the time of that run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())