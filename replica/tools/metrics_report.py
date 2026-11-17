"""Single source of truth for every "current value" this project quotes.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
The five metrics scripts each print their own shape -- `real gap : N`, `types with scope misses: N`,
`total mismatches: N`, a 19-row table, two section counts -- so every document that wants to quote
"the current number" re-typed it by hand. That is how AGENTS.md §4, GOAL.md, HANDOFF.md,
SESSION_STATE.md and DEVIATIONS.md drifted apart (R433 found eight stale figures in six files while
the tools themselves were correct). A number that lives in six places is a number that will be wrong
in five of them.

So: run the five scripts in one process, capture their raw output verbatim, and write ONE generated
file -- docs/METRICS.md -- that carries the timestamp, the exact command per metric, and a parsed
summary table. Documents then cite `docs/METRICS.md` instead of hard-coding a value, and "what is
the number now" stops being a discipline question and becomes a generation question.

Reproduce:
    cd replica
    python tools/metrics_report.py                  # five metrics + full suite
    python tools/metrics_report.py --skip-tests     # five metrics only (no build, ~2 s)
    python tools/metrics_report.py --out ../docs/METRICS.md

Side effects of the metrics themselves (not of this wrapper): copy_audit_report.py rewrites
docs/COPY_QUEUE.md; copy_audit_report.py and the others only read src/.

Exit code: 0 when every metric script exited 0 (and, with tests, the suite passed). A non-zero exit
is reported in the file and returned here -- "could not run" is never recorded as "passed".
"""

import argparse
import datetime
import io
import os
import re
import subprocess
import sys

# R834: the pattern table sits inside summary_bits, so the orphan check reads this file's own text.
PATTERN_SOURCE = open(__file__, encoding="utf-8").read()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_OUT = os.path.abspath(os.path.join(ROOT, "..", "docs", "METRICS.md"))
DOTNET = os.environ.get("DOTNET", r"D:\tools\dotnet8\dotnet.exe")

METRICS = [
    ("名字级绑定缺口", ["tools/bind_diff.py", "--buckets"], ["real gap", "missing"]),
    ("类型级绑定缺口", ["tools/bind_scope.py"], ["types with scope misses"]),
    ("类型缺失（type presence）", ["tools/bind_diff.py", "--type-presence"], ["types absent from source"]),
    # R888: the total is dominated by Cybersole.Ui, which the priority order defers behind checkout
    # flows, anti-bot and the request layer. Of the ninety-four rows, seventy-seven are Ui, seventeen
    # are Core or Services, and Stores carries none. The core figure is the one steering should read.
    ("成员形状差异", ["tools/shape_audit.py", "--baseline"],
     ["total mismatches", "core mismatches"]),
    ("文案缺口总表", ["tools/copy_audit_report.py"], ["copy: zones with a missing key"]),
    ("绑定缺口分桶", ["tools/backlog_report.py"], ["backlog: classes missing members", "backlog: types absent"]),
    # R466 fifth metric. Reads the TSV written by analysis/binding_descriptors.py (IDA-dependent, slow);
    # this wrapper stays fast and fails loudly when the TSV is missing rather than reporting zeros.
    ("原版绑定描述符表", ["tools/descriptor_report.py"], ["descriptor entries", "descriptor types", "only in descriptors", "only in xaml table"]),
    # R600 sixth metric: the persisted-data file names, which the other entries do not look at.
    # R834: every entry now names the pattern keys it owns, so summary_bits can only fill that metric's row.
    # A loose pattern can no longer put a number in a neighbour's line.
    ("数据文件名对照", ["tools/datafiles_diff.py"], ["datafiles: original-on-disk not in replica", "datafiles: replica-only"]),
    # R832 seventh metric: the goal's first clause is that the function counts be equal, and until then
    # nothing here measured it -- the six above count declarations, this one counts the artifacts.
    ("函数数量（.pdata）", ["tools/func_count.py"], ["functions: original .pdata", "functions: replica .pdata", "functions: ratio"]),
    # R932: the function ratio comes from .publish-aot, so whether that artifact matches the current source is
    # part of reading the number. Criterion (c) asks for a recomputable artifact comparison; a stale artifact
    # makes it recomputable but about the wrong build.
    ("产物陈旧度（.publish-aot vs src）", ["tools/artifact_freshness.py"], ["source files newer than the artifact", "lines in those files"]),
    # R921: criterion (f) has two columns and only the store one had been measured. These add the vendor column, so the
    # coverage table the criterion asks for comes out of the single number source instead of being assembled by hand.
    ("核心覆盖：store 宿主", ["tools/core_coverage.py"], ["hosts with a path", "store hosts", "store hosts matched", "store hosts unmatched", "vendor hosts"]),
    ("核心覆盖：vendor 宿主", ["tools/vendor_coverage.py"], ["vendor hosts carrying a path", "vendors named somewhere in src", "vendors absent from src"]),
    # R977: criterion (c) is "artifact-level comparison recomputable". func_count answers how many, and those two answer
    # how much and where -- figures R969 through R972 measured by hand and then quoted from prose, which is how a number
    # drifts. Both were already tools; nothing here is new capability, only registration.
    ("可执行段体量", ["tools/pe_sections.py"],
     ["section-mass: original executable", "section-mass: replica executable", "section-mass: ratio"]),
    ("函数分布（.pdata 地址分桶）", ["tools/pdata_sections.py"],
     ["pdata: above boundary original", "pdata: above boundary replica", "pdata: last replica bucket"]),
    # R982: criterion (e) says the mutation tests all fire, and that figure lived only in prose -- which is how the handoff
    # block R979 caught came to quote a hundred-and-fifty-round-old suite total. A full mutation pass takes about twelve
    # minutes and this wrapper is run every round, so it cannot be measured here. What it can do is read the dated record
    # that pass writes and report how far the tree has moved since, so the number carries its own caveat.
    ("变异套件（上次运行）", ["tools/mutation_report.py"],
     ["mutation-fit: total", "mutation-fit: fired", "mutation-fit: decorative", "mutation-fit: skipped",
      "mutation-fit: staleness"]),
]

SCOPE_NOTE = "note: base-class inheritance is counted (by design since R343)"


def run(argv, timeout=1800):
    command = " ".join(argv)
    try:
        done = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout)
        return done.returncode, command, done.stdout, done.stderr
    except FileNotFoundError as exc:
        return 127, command, "", "missing executable: %s" % exc
    except subprocess.TimeoutExpired:
        return 124, command, "", "timeout after %ss" % timeout


def summary_bits(name_out, owned):
    """Pull the headline numbers, but only the ones this metric owns.

    R834: the caller passes the keys from its METRICS entry. Before this every pattern ran against every
    script's output, so a loose one could fill a neighbouring metric's row with a number that was correct
    in itself and belonged somewhere else. Ownership makes that impossible rather than merely detectable.
    """
    found = {}
    patterns = {
        "real gap": r"real gap\s*:\s*(\d+)",
        "missing": r"\nmissing:\s*(\d+)",
        "types with scope misses": r"types with scope misses:\s*(\d+)",
        "types absent from source": r"type presence: \d+ declared in bindings, \d+ present in source, (\d+) absent",
        "total mismatches": r"total mismatches:\s*(\d+)",
        # R921: criterion (f) -- the core coverage table has two columns and these are their figures.
        "hosts with a path": r"hosts with a path:\s*(\d+)",
        "store hosts": r"(?:^|\\n)store hosts:\s*(\d+)",
        "store hosts matched": r"store hosts matched:\s*(\d+)",
        "store hosts unmatched": r"store hosts unmatched:\s*(\d+)",
        "vendor hosts": r"(?:^|\\n)vendor hosts:\s*(\d+)",
        "vendor hosts carrying a path": r"vendor hosts carrying a path:\s*(\d+)",
        "vendors named somewhere in src": r"vendors named somewhere in src:\s*(\d+)",
        "vendors absent from src": r"vendors absent from src:\s*(\d+)",
        # R888: the same audit's rows restricted to Stores, Services, Http and Core. The total is
        # dominated by Ui, so this is the figure that tracks progress on the deferred-behind work.
        "core mismatches": r"core mismatches:\s*(\d+)",
        "copy: zones with a missing key": r"^\s+(\S+)\s+\d+\s+(\d+) missing",
        "backlog: classes missing members": r"classes that EXIST in the replica but miss members:\s*(\d+)",
        "backlog: types absent": r"types that DO NOT exist \(structural\):\s*(\d+)",
        # R466 fifth metric
        "descriptor entries": r"descriptor entries\s*:\s*(\d+)",
        "descriptor types": r"descriptor types\s*:\s*(\d+)",
        "only in descriptors": r"only in descriptors\s*:\s*(\d+)",
        "only in xaml table": r"only in xaml table\s*:\s*(\d+)",
        # R600 sixth metric; R602 switched its original side to the data directory (see the tool's header)
        "datafiles: original-on-disk not in replica": r"original-on-disk but not written by the replica\s*:\s*(\d+)",
        "datafiles: replica-only": r"replica-referenced, found in neither source\s*:\s*(\d+)",
        # R832 seventh metric. Unique prefixes on purpose: summary_bits runs every pattern against every
        # script, and a bare "replica:" matched datafiles_diff.py output, so that metric reported a function
        # count of zero. A label no other script can emit is the fix; loosening or tightening the regex is not.
        "functions: original .pdata": r"pdata-original:\s*([\d,]+)",
        "functions: replica .pdata": r"pdata-replica:\s*([\d,]+)",
        "functions: ratio": r"pdata-ratio:\s*([\d.]+%)",
        # R932: artifact freshness, so the function ratio is never quoted as current without this beside it.
        "source files newer than the artifact": r"source files newer than the artifact:\s*(\d+)",
        "lines in those files": r"lines in those files:\s*(\d+)",
        # R977: the two figures that make criterion (c)'s comparison complete. Prefixed so no other script can own them.
        "section-mass: original executable": r"section-mass-original-executable:\s*(\d+)",
        "section-mass: replica executable": r"section-mass-replica-executable:\s*(\d+)",
        "section-mass: ratio": r"section-mass-ratio:\s*([\d.]+%)",
        "pdata: above boundary original": r"pdata-above-0x1C00000-original:\s*(\d+)",
        "pdata: above boundary replica": r"pdata-above-0x1C00000-replica:\s*(\d+)",
        "pdata: last replica bucket": r"pdata-last-replica-bucket:\s*(0x[0-9A-Fa-f]+)",
        # R982: the mutation record, plus how stale it is. Staleness is the field that matters most -- without it the
        # counts read as current when they may describe a tree several edits old.
        "mutation-fit: total": r"mutation-fit-total:\s*(\d+)",
        "mutation-fit: fired": r"mutation-fit-fired:\s*(\d+)",
        "mutation-fit: decorative": r"mutation-fit-decorative:\s*(\d+)",
        "mutation-fit: skipped": r"mutation-fit-skipped:\s*(\d+)",
        "mutation-fit: staleness": r"mutation-fit-staleness:\s*(.+)",
    }
    for label, pattern in patterns.items():
        if label not in owned:
            continue
        hits = re.findall(pattern, name_out, re.M)
        if label.startswith("copy:"):
            total = sum(int(m) for _, m in hits)
            zones = sum(1 for _, m in hits if int(m) > 0)
            if hits:
                found[label] = "%d (in %d zone[s])" % (total, zones)
        elif hits:
            found[label] = hits[-1] if isinstance(hits[-1], str) else hits[-1][0]
    return found


def _free_memory_gb():
    """Free physical memory in GB, or None when it cannot be read (R684)."""
    try:
        import ctypes

        class _MS(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = _MS()
        stat.dwLength = ctypes.sizeof(_MS)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return None
        return stat.ullAvailPhys / (1024.0 ** 3)
    except Exception:
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-tests", action="store_true", help="do not run the full xunit suite")
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    # R684: the session ran out of memory and the machine was restarted. This wrapper is the command run every
    # round, and the full suite builds and loads a test assembly each time, so it refuses to start when the box is
    # already tight -- adding load to a starved machine is how a round turns into a reboot. The project rule is
    # 2 GB for builds and 1 GB to stop entirely; the floor here is the stop line, and --skip-tests is exempt
    # because it builds nothing.
    if not args.skip_tests:
        gb = _free_memory_gb()
        if gb is not None:
            print("  free memory: %.2f GB" % gb)
            if gb < 1.0:
                raise SystemExit(
                    "free memory %.2f GB is below 1.0 GB -- free memory before running the suite, "
                    "or pass --skip-tests to refresh the metrics only" % gb
                )
            if gb < 2.0:
                print("  WARNING: below the 2 GB build floor; the suite will run with -m:1 only")

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime("%Y-%m-%d %H:%M:%S %z")

    results = []
    worst = 0
    # R502: copy_audit_report.py finishes its work and then dies during interpreter shutdown (exit -1 /
    # 0xC0000005). Its rows and file may or may not reach the buffer before that, so neither the exit code nor
    # stdout is a reliable verdict. What it *produces* is: if the target file was rewritten during the call, the
    # metric ran. That is the check.
    # R979: this used to be a path relative to whatever cwd the caller happened to have, so the fallback engaged from
    # replica/ and silently did not from the repo root -- and the other scripts in this repo are documented to be run
    # from both. A verdict path that depends on where you stand is not a verdict. It is now anchored to ROOT.
    VERDICT_BY_FILE = {"文案缺口总表": os.path.join(ROOT, "docs", "COPY_QUEUE.md")}
    for title, script_args, owned in METRICS:
        watched = VERDICT_BY_FILE.get(title)
        before = os.path.getmtime(watched) if watched and os.path.exists(watched) else None
        code, command, out, err = run([sys.executable] + script_args)
        ok = code == 0
        if not ok and watched:
            after = os.path.getmtime(watched) if os.path.exists(watched) else None
            ok = after is not None and (before is None or after > before)
        worst = max(worst, 0 if ok else code)
        results.append({"title": title, "command": command, "code": code,
                        "out": out, "err": err, "bits": summary_bits(out, owned),
                        # R834: carried so the report can state what the row is allowed to contain
                        "owned": owned})

    tests = None
    if not args.skip_tests:
        # R493: the browser-dependent classes are excluded from the default run, and named so the exclusion is
        # visible. They drive a real Chrome through CDP (`ChromiumBridge.LaunchAsync`), each takes ~2 minutes when
        # the endpoint doesn't come up, and on 2026-11-14 a full run of them contributed to the machine running out
        # of memory and rebooting mid-session. Run them deliberately, one class at a time:
        #   dotnet test --filter "FullyQualifiedName~VoiceListTests"
        browser_filter = ("Speed!=Slow"
                          "&FullyQualifiedName!~VoiceListTests"
                          "&FullyQualifiedName!~GlobalSurfaceTests"
                          "&FullyQualifiedName!~KeyOrderDispatchTests"
                          "&FullyQualifiedName!~PatchJournalTests"
                          "&FullyQualifiedName!~PruneWhitelistTests"
                          "&FullyQualifiedName!~NetworkRecorderLiveTests"
                          # R555: ChromiumStealthTests also drives a real Chrome — it asserts on the
                          # fingerprint a launched instance reports (`typeof navigator.something`).
                          # Without a live endpoint it fails with "Expected: object / Actual: undefined",
                          # which says nothing about the replica. It belongs with the classes above.
                          "&FullyQualifiedName!~ChromiumStealthTests")
        code, command, out, err = run([
            DOTNET, "test", "tests/Cybersole.Tests/Cybersole.Tests.csproj", "-c", "Debug",
            "--filter", browser_filter, "-m:1"], timeout=3600)
        worst = max(worst, 0 if code == 0 else code)
        m = re.search(r"失败:\s*(\d+)，通过:\s*(\d+)，已跳过:\s*(\d+)，总计:\s*(\d+)", out)
        tests = {"command": command, "code": code,
                 "failed": m.group(1) if m else "?",
                 "passed": m.group(2) if m else "?",
                 "skipped": m.group(3) if m else "?",
                 "total": m.group(4) if m else "?",
                 "out": out, "err": err}
        if not m:
            tests.update({"failed": "unparsed", "passed": "unparsed", "skipped": "unparsed", "total": "unparsed"})

    # the scope note must be visible in the generated file, not only in the script
    if SCOPE_NOTE not in results[1]["out"]:
        results[1]["err"] = (results[1]["err"] + "\n" if results[1]["err"] else "") + \
            "WARNING: bind_scope.py did not print the scope note; the script predates the R433 decision."

    lines = []
    lines.append("# 度量快照（生成文件，请勿手改）")
    lines.append("")
    lines.append("> 本文件由 `python tools/metrics_report.py` 生成。")
    lines.append("> **所有文档里的「当前值」都引用本文件，不再各自硬编码。**")
    lines.append("> 要更新：重跑生成命令即可；手改本文件会在下一次生成时被覆盖。")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append("| 生成时间 | %s |" % stamp)
    lines.append("| 工作目录 | `%s` |" % ROOT)
    lines.append("| 生成命令 | `python tools/metrics_report.py%s` |" % ("" if not args.skip_tests else " --skip-tests"))
    lines.append("| 度量脚本结果 | %s |" % ("全部 exit 0" if all(r["code"] == 0 for r in results) else "**有非零退出，见下**"))
    if tests is not None:
        lines.append("| 完整套件 | **%s 通过 / %s 失败 / %s 跳过 / %s 总计** |"
                     % (tests["passed"], tests["failed"], tests["skipped"], tests["total"]))
    else:
        lines.append("| 完整套件 | 本次跳过（`--skip-tests`） |")
    lines.append("")
    lines.append("## 摘要素值")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|---|---|")
    for r in results:
        if not r["bits"]:
            lines.append("| %s | （未解析，见下方原始输出） |" % r["title"])
            continue
        for label, value in r["bits"].items():
            lines.append("| %s — %s | %s |" % (r["title"], label, value))
    lines.append("")

    # R834: a pattern no entry owns is never extracted, so say so in the file rather than losing it silently.
    owned_all = {k for r in results for k in r.get("owned", [])}
    declared = set(re.findall(r'^\s{8}"([^"]+)": r"', PATTERN_SOURCE, re.M))
    for orphan in sorted(declared - owned_all):
        lines.append("**WARNING: pattern owned by no metric, so never extracted: `%s`**" % orphan)
        lines.append("")

    lines.append("## 逐条命令与原始输出")
    lines.append("")
    for r in results:
        lines.append("### %s" % r["title"])
        lines.append("")
        lines.append("```")
        lines.append("cd %s" % ROOT)
        lines.append(r["command"])
        lines.append("```")
        lines.append("")
        lines.append("`exit %d`" % r["code"])
        lines.append("")
        if r["out"].strip():
            lines.append("```text")
            lines.append(r["out"].rstrip())
            lines.append("```")
        if r["err"].strip():
            lines.append("")
            lines.append("stderr:")
            lines.append("")
            lines.append("```text")
            lines.append(r["err"].rstrip())
            lines.append("```")
        lines.append("")

    if tests is not None:
        lines.append("### 完整套件")
        lines.append("")
        lines.append("```")
        lines.append("cd %s" % ROOT)
        lines.append(tests["command"])
        lines.append("```")
        lines.append("")
        lines.append("`exit %d` · %s 通过 / %s 失败 / %s 跳过 / %s 总计"
                     % (tests["code"], tests["passed"], tests["failed"],
                        tests["skipped"], tests["total"]))
        lines.append("")
        tail = [l for l in tests["out"].splitlines() if l.strip()][-15:]
        if tail:
            lines.append("```text")
            lines.extend(tail)
            lines.append("```")
            lines.append("")
        if tests["err"].strip():
            lines.append("stderr:")
            lines.append("")
            lines.append("```text")
            lines.append(tests["err"].rstrip())
            lines.append("```")
            lines.append("")
    else:
        lines.append("### 完整套件")
        lines.append("")
        lines.append("本次未运行（`--skip-tests`）。**这不等于通过**：判据 e 需要它。")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 谁引用本文件")
    lines.append("")
    lines.append("`AGENTS.md §4` · `docs/GOAL.md` 判据 a · `docs/HANDOFF.md` · `docs/COPY_QUEUE.md` 头部 ·")
    lines.append("`replica/docs/SESSION_STATE.md` · `replica/docs/DEVIATIONS.md`。")
    lines.append("")
    lines.append("`replica/docs/VERDICT.md` **不引用也不修改** —— 它是按轮次的历史记录。")
    lines.append("")

    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    io.open(out_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("wrote %s" % out_path)
    for r in results:
        print("  %-22s exit %d  %s" % (r["title"], r["code"], r["bits"] or ""))
    if tests is not None:
        print("  %-22s exit %d  %s 通过 / %s 失败 / %s 跳过"
              % ("完整套件", tests["code"], tests["passed"], tests["failed"], tests["skipped"]))
    return 0 if worst == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
