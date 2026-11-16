"""Finish R824: update the handoff's second item and commit. (R824)

The record run appended to all four documents and then died on a missing import before reaching the handoff edit and the
commit, so the documents are written but untracked. This does the two remaining steps and verifies the markers.
"""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

OLD = ("2. **`StoreFlow.HandleResponseAsync` 是死代码** —— 有定义、无调用点，读 `lastStatus` 并按状态码分支。\n"
       "   **它看起来该被某步调用。谁该调它，是下一个要查的。**")

NEW = ("2. **两个真死步骤（R824 已确认）**：`HandleResponseAsync` 与 `RefreshSessionAsync`，"
       "总提及都是 1（只有自己的声明）。\n"
       "   `StoreFlowParityTests` 的规范步骤表含 `RefreshSession`/`VerifySession` → **镜像有这些阶段**。\n"
       "   **下一步：读反编译，看 `RefreshSession` 挂在哪个时刻。猜一个调用点 = 假覆盖（R799）。**")

h = io.open(HANDOFF, encoding="utf-8").read()
if OLD in h:
    io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h.replace(OLD, NEW, 1))
    print("  handoff item 2 updated")
elif "R824 已确认" in h:
    print("  handoff already updated")
else:
    print("  handoff anchor not found — appending a note instead")
    io.open(HANDOFF, "a", encoding="utf-8").write(
        "\n## R824 补充\n\n"
        "**两个真死步骤**：`HandleResponseAsync` 与 `RefreshSessionAsync`，总提及都是 1（只有自己的声明）。\n"
        "`StoreFlowParityTests` 的规范步骤表含 `RefreshSession`/`VerifySession` → 镜像有这些阶段。\n"
        "**下一步：读反编译，看 `RefreshSession` 挂在哪个时刻。猜一个调用点 = 假覆盖（R799）。**\n")

ok = True
for rel, key in (("docs/BLOCKERS.md", "R824"), ("docs/DELIVERY_STATUS.md", "R824"),
                 ("replica/docs/VERDICT.md", "第 824 轮"), ("replica/docs/BINDING_BACKLOG.md", "R824"),
                 ("docs/HANDOFF.md", "R824")):
    body = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="surrogateescape").read()
    present = key in body
    ok = ok and present
    print("  verify %-34s %s" % (rel, present))

if not ok:
    print("  REFUSING to commit: a record is missing")
    raise SystemExit(1)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R824: two canonical steps are declared and never invoked\n\n"
     "The handoff asked whether HandleResponseAsync is dead weight or a stage the runner should drive. Answering it took"
     " two failed scans and one working criterion.\n\n"
     "Searching StoreFlowRunner for `flow.<name>` reported 137 of 165 declared steps never invoked; widening to every"
     " file for `\\w+.<name>` reported 136. Both are wrong, and the counter-example is one line: FindProductFlowAsync"
     " delegates with `=> FindProductAsync(c, ct)`, unqualified, so a pattern requiring a receiver dot misses it."
     " FindProductAsync has twenty-seven mentions and fourteen overrides and both scans called it nowhere. Same family as"
     " R822: assume a shape, then read what does not fit as absent.\n\n"
     "What works assumes no call shape. Count bare-name occurrences: anything used in any form appears at least twice."
     " HandleResponseAsync appears once, in its own declaration; so does RefreshSessionAsync. VerifySessionAsync appears"
     " three times, twice as overrides, with no call site. Two steps are provably dead.\n\n"
     "Both matter. StoreFlowParityTests pins a canonical list containing RefreshSession and VerifySession, so the image"
     " has those stages and the replica declares without reaching them. RefreshSessionAsync's comment calls it the cheap"
     " GET that keeps the session cookie warm between polls, so never invoking it means a long poll lets the session go"
     " cold -- a gap in priority one, not decoration.\n\n"
     "I did not wire it: where the stage belongs needs the decompilation, and memory is 1.22 GB after the restart so IDA"
     " stayed shut. A guessed insertion point yields coverage that looks implemented, which is R799's lesson.\n\n"
     "Unknown: which moment carries RefreshSession in the image; whether HandleResponseAsync has any counterpart there,"
     " since the canonical list omits it and it may be replica-only; and the real status of the other 163 declarations,"
     " because a bare count of one proves dead and cannot prove alive.\n\n"
     "No product code changed; suite not run under the memory discipline; metrics carried at 4 / 0 / 17 / 78 / 0."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
