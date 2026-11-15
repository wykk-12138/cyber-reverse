"""Classify every remaining dead copy entry by whether a HOST exists at all. (R660)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); this reads the
replica's source only.

**Why**: the CSV-editor family has been resolved one entry at a time -- R631/R632/R653/R654 added five, R651 closed one
as host-less. Doing the remaining 32 that way would take 32 rounds and produce 32 separate notes. This does the whole
set in one pass, and the only question asked is the cheapest one: **does the class contain anything that could produce
this sentence?**

**Definition, fixed before measuring**: for each dead entry, a keyword is derived from its name (see `KEYWORDS`).
Then:

  * **NO HOST** -- the keyword appears **nowhere** in the class body. There is no code that could ever say this
    sentence; implementing it would mean adding a whole feature, and its behaviour is Unknown.
  * **HOST?** -- the keyword does appear. That means some code path exists, and the entry may be implementable once
    its rule is known -- but this test does **not** claim the host is the right one.

The keyword choice is deliberately mechanical and therefore crude; a "HOST?" result means "worth a look", not
"implementable", and a "NO HOST" result is only reported when the keyword is absent outright.

Read-only. Prints; writes nothing.
"""

import io
import os
import re
import sys

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
DOC = r"D:\projects\cyber-reverse\docs\DEAD_COPY.md"

KEYWORDS = {
    "AddRow": ["AddRow", "Add Row", "Insert("],
    "AllColumns": ["AllColumns", "All columns"],
    "Apply": ["ApplyCore", "Apply Changes"],
    "Clipboard": ["Clipboard"],
    "ConfirmDeleteFormat": ["ConfirmDelete", "delete {0} profiles"],
    "DeleteRows": ["DeleteRows", "Delete Rows", "RemoveAt"],
    "Duplicate": ["Duplicate"],
    "Export": ["Export"],
    "Find": ["Find"],
    "Hint": ["Hint"],
    "Import": ["Import"],
    "MenuClear": ["MenuClear", "Clear("],
    "MenuCopy": ["MenuCopy", "Copy("],
    "MenuFillDown": ["FillDown", "Fill Down"],
    "MenuPaste": ["MenuPaste", "Paste("],
    "ModeGrid": ["ModeGrid", "Mode.Text", "Mode.Text"],
    "ModeText": ["ModeText"],
    "Regex": ["Regex"],
    "ReplaceAll": ["ReplaceAll", "Replace("],
    "ReplaceWith": ["ReplaceWith"],
    "StatusDiscardConfirm": ["DiscardConfirm", "unsaved"],
    "StatusExported": ["Export"],
    "StatusIgnoredColumns": ["IgnoredColumns"],
    "StatusImported": ["Merged", "StatusImported"],
    "StatusNoHeader": ["NoHeader"],
    "StatusParseFailed": ["ParseFailed", "catch"],
    "StatusRegexInvalid": ["RegexInvalid", "Regex"],
    "StatusReplaced": ["Replaced"],
    "SummaryEdited": ["SummaryEdited", "Summary"],
    "SummaryErrors": ["SummaryErrors", "Summary"],
    "SummaryNew": ["SummaryNew", "Summary"],
    "SummaryNone": ["SummaryNone", "Summary"],
    "SummaryRemoved": ["SummaryRemoved", "Summary"],
    "Undo": ["Undo"],
}


def main():
    raw = io.open(SRC, encoding="utf-8", errors="replace").read()
    # R662: the search must be the CLASS, not the file. `ProfileGroupView` and `SplitCsv` live in the same file and
    # supplied `RemoveAt` / `Clear(` as hosts for entries that the CSV editor cannot produce.
    decl = re.compile(r"^\s*(?:public|internal|private)?\s*(?:sealed\s+|static\s+|partial\s+|abstract\s+)*(?:class|record|struct)\s+(\w+)")
    lines_all = raw.splitlines()
    marks = [(i, m.group(1)) for i, line in enumerate(lines_all, 1) if (m := decl.match(line))]
    target = next((k for k, (_ln, nm) in enumerate(marks) if nm == "ProfileCsvEditorView"), None)
    if target is None:
        raise SystemExit("ProfileCsvEditorView not found")
    lo = marks[target][0]
    hi = marks[target + 1][0] - 1 if target + 1 < len(marks) else len(lines_all)
    raw = "\n".join(lines_all[lo - 1:hi])
    print("class range: %d..%d (%d bytes)" % (lo, hi, len(raw)))
    # R660b: the keyword search must not see the dead table itself -- ["AddRow"] = "Add Row" is a TABLE ENTRY,
    # and counting it as a code path made 31 of 32 look hosted in the first version of this script.
    # R662b: line scan with brace counting. The regex version left rows behind (`["Import"] = "Import CSV"` survived)
    # because the table's closing brace is not formatted the way the pattern assumed.
    _out, _inside, _depth = [], False, 0
    for line in raw.splitlines():
        if not _inside and "IReadOnlyDictionary<string, string> Copy" in line:
            _inside = True
            _depth = line.count("{") - line.count("}")
            _out.append("")
            continue
        if _inside:
            _depth += line.count("{") - line.count("}")
            if _depth <= 0:
                _inside = False
            continue
        _out.append(line)
    text = "\n".join(_out)
    print("dictionary stripped: %d -> %d bytes" % (len(raw), len(text)))

    dead = []
    for line in io.open(DOC, encoding="utf-8").read().splitlines():
        m = re.match(r"\|\s*\d+\s*\|\s*`(\w+)`\s*\|", line)
        if m:
            dead.append(m.group(1))

    print("dead entries per docs/DEAD_COPY.md: %d" % len(dead))
    print()

    no_host = []
    host = []
    for name in dead:
        kws = KEYWORDS.get(name)
        if kws is None:
            no_host.append((name, "(no keyword defined)"))
            continue
        found = [k for k in kws if k in text]
        if found:
            host.append((name, found))
        else:
            no_host.append((name, "none of %s" % kws))

    print("=== HOST? (%d) -- some code path may exist ===" % len(host))
    for name, found in host:
        print("  %-24s %s" % (name, found))

    print()
    print("=== NO HOST (%d) -- the keyword appears nowhere ===" % len(no_host))
    for name, why in no_host:
        print("  %-24s %s" % (name, why))

    print()
    print("summary: %d host-less, %d worth a look, of %d" % (len(no_host), len(host), len(dead)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
