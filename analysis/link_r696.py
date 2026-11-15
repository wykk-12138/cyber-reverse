"""R696: cross-link the two documents and make wait_ready.py self-explaining.

The lesson from R695 was that the trap was already documented and I still walked into it. So the fix is not another
paragraph -- it is to put the pointer where the next action happens:

  1. `PARITY_PRODUCT.md` §8 (the R433 record) gains a pointer to the operational checklist and to the tool.
  2. `IDA_STARTUP_CHECKLIST.md` gains a pointer back to the historical record, so the two stop being parallel copies.
  3. `analysis/wait_ready.py`'s header says which earlier criterion it replaces and why that one was insufficient --
     because the intermediate state is *stable*, so "two identical samples" can both be wrong.

No history is rewritten: the R433 paragraph keeps its text and gains a pointer beneath it.
"""

import io
import subprocess

PARITY = r"D:\projects\cyber-reverse\docs\PARITY_PRODUCT.md"
CHECKLIST = r"D:\projects\cyber-reverse\docs\IDA_STARTUP_CHECKLIST.md"
WAITER = r"D:\projects\cyber-reverse\analysis\wait_ready.py"

PARITY_ANCHOR = "> 判据是**窗口标题不再带 `Loading`** 且**连续两次取值相同**（187,328 两次一致）。"

PARITY_ADD = """

> **R696 指引（这一段是操作手册，不是历史）**：这条坑现在有两处入口 ——
> 启动步骤见 `docs/IDA_STARTUP_CHECKLIST.md` 的「三半、端口开 ≠ 分析完」，
> 就绪判定用 `python analysis/wait_ready.py <port> <timeout>`（轮询 `auto_analysis_ready`）。
> **为什么"两次取值相同"不够**：那个中间态是**稳定**的 —— R433 的错误/正确比值 0.730 与 R694 的 0.730 相隔 260 多轮仍一致，
> 所以两次取样很可能取到同一个偏小数。**只认标志，不认一致性。**"""

CHECKLIST_ANCHOR = "55 MB AOT 实测 **320 秒**。端口一起就导出的后果见 `BLOCKERS.md` §127（得出 9/819 的中间值）。"

CHECKLIST_ADD = """

**历史记录在** `docs/PARITY_PRODUCT.md` §8「踩过的坑（R433）」：那次是 136,798 → 187,328，
比值 **0.730**；R694 是 136,989 → 187,732，比值**同样 0.730**。
**两处说的是同一个中间态** —— 本清单是操作入口，那边是原始记录。
**注意那边的判据「窗口标题不带 Loading + 连续两次取值相同」已被本清单的 `auto_analysis_ready` 取代**：
稳定性意味着两次一致性不能证明正确（见 `analysis/wait_ready.py` 文件头）。"""

WAITER_OLD_DOC = '''"""Wait for an IDA instance's auto-analysis to finish, judged by the readiness flag. (R694)

Port-open is the wrong signal: the plugin answers as soon as it is loaded, while analysis is still running. This polls
`server_health.auto_analysis_ready` and exits 0 only when it flips to true.

Usage: python analysis/wait_ready.py [port] [timeout_sec]
"""'''

WAITER_NEW_DOC = '''"""Wait for an IDA instance's auto-analysis to finish, judged by the readiness flag. (R694, documented R696)

Port-open is the wrong signal: the plugin answers as soon as it is loaded, while analysis is still running. This polls
`server_health.auto_analysis_ready` and exits 0 only when it flips to true.

**This replaces two earlier criteria, and the reason matters:**

  * R433 used "the window title no longer says Loading" plus "two consecutive samples agree". The second half does not
    work: the intermediate state is *stable*. R433's wrong/right ratio was 136,798/187,328 = 0.730; R694's was
    136,989/187,732 = 0.730, 260 rounds later. Two samples in that window can agree and both be wrong.
  * R613 already polled `auto_analysis_ready`, so the good criterion existed before this file did -- it just lived in a
    report instead of in the code that takes the measurement. Keeping it here is the point.

Operational steps: `docs/IDA_STARTUP_CHECKLIST.md` ("端口开 ≠ 分析完"). Original record: `docs/PARITY_PRODUCT.md` §8.

Usage: python analysis/wait_ready.py [port] [timeout_sec]
"""'''


def main():
    ok = 0

    body = io.open(PARITY, encoding="utf-8").read()
    if "R696 指引" in body:
        print("  parity: already linked")
    elif PARITY_ANCHOR in body:
        io.open(PARITY, "w", encoding="utf-8").write(
            body.replace(PARITY_ANCHOR, PARITY_ANCHOR + PARITY_ADD, 1))
        print("  parity: pointer added")
        ok += 1
    else:
        print("  parity: MISS anchor")

    body = io.open(CHECKLIST, encoding="utf-8").read()
    if "历史记录在" in body:
        print("  checklist: already linked")
    elif CHECKLIST_ANCHOR in body:
        io.open(CHECKLIST, "w", encoding="utf-8").write(
            body.replace(CHECKLIST_ANCHOR, CHECKLIST_ANCHOR + CHECKLIST_ADD, 1))
        print("  checklist: pointer added")
        ok += 1
    else:
        print("  checklist: MISS anchor")

    body = io.open(WAITER, encoding="utf-8").read()
    if "This replaces two earlier criteria" in body:
        print("  wait_ready: already documented")
    elif WAITER_OLD_DOC in body:
        io.open(WAITER, "w", encoding="utf-8").write(body.replace(WAITER_OLD_DOC, WAITER_NEW_DOC, 1))
        print("  wait_ready: header rewritten")
        ok += 1
    else:
        print("  wait_ready: MISS docstring")

    # prove the tool still parses and the docstring is what we think
    import ast
    tree = ast.parse(io.open(WAITER, encoding="utf-8").read())
    doc = ast.get_docstring(tree) or ""
    print()
    print("  wait_ready.py parses OK; docstring mentions R433: %s, stable: %s"
          % ("R433" in doc, "stable" in doc))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R696: cross-link the readiness trap into the place where the measurement happens\n\n"
         "PARITY_PRODUCT (record) <-> IDA_STARTUP_CHECKLIST (manual) <-> wait_ready.py (code).\n"
         "The waiter's header now names the two criteria it replaces and why 'two identical samples'\n"
         "is insufficient: the intermediate state is stable, 0.730 wrong/right in both R433 and R694.\n"
         "Keeping the correct criterion in the code that takes the measurement, not only in a report,\n"
         "is the actual fix for having repeated a documented mistake."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True,
    )
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:200]))
    print("edits applied: %d" % ok)


if __name__ == "__main__":
    main()
