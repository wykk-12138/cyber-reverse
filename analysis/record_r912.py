"""Record R912: recovery became a command, and the two suite figures were reconciled."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 恢复变成一条命令；并且我核清了两个套件数为什么不一致（R912）

**R911 的教训是「记错一个目录名就等于没有快照」。这一轮把那句话变成代码。**

### `snapshot.py` 加了两个模式

```
python tools/snapshot.py --list                     列出所有快照
python tools/snapshot.py --restore <stamp> [rel]    恢复一个文件或整份
```

**四种行为都实测过：**

| 情形 | 结果 |
|---|---|
| `--list` | 41 份 / 11,770 文件 / 109.5 MB，**并打印实际目录** |
| 恢复一个不存在的文件 | `not in that snapshot` + `restored 0`，**不写任何东西** |
| 恢复越界路径 `..\\..\\outside.cs` | 拒绝，`restored 0` |
| 恢复真实文件 | `restored 1`，而 `StoreFlow` 虚步骤仍是 **175** |

**而 `--list` 会打印那个真实路径 `tools/.snapshots` —— 这是刻意的：
R911 我不是不知道怎么恢复，是**记错了目录名**。所以让命令自己说路径。**

### 一处我该说清的：越界拒绝是被前一个检查挡住的

**`..\\..\\outside.cs` 报的是 `not in that snapshot`，不是我的路径守卫。
因为那个文件在快照里不存在，所以先被存在性检查拒绝了。**

**所以路径守卫（`dst.startswith(ROOT + sep)`）**只对「快照里存在、但会写到树外」的情形生效** ——
而快照里不会有那种路径。那行守卫**实际上不可达**。**

**留着它是对的还是多余的？我留着，因为快照的来源是 `os.walk(src)`，而如果将来有人改了快照内容，
守卫是唯一挡住写入树外的东西。但它现在不验证任何东西，这一点必须写出来。**

### 而两个套件数，我核过了

**`metrics_report.py` 报 1815；直接跑全量报 2113 通过 / 2 跳过。差 298。**

**原因（R493 的设计，不是新问题）：`metrics_report.py` 排除六个依赖真 Chrome 的类**
（`VoiceListTests` · `GlobalSurfaceTests` · `KeyOrderDispatchTests` · `PatchJournalTests` ·
`PruneWhitelistTests` · `NetworkRecorderLiveTests`），
**因为 2026-11-14 连着跑几轮全量把整机内存耗尽、系统重启。**

**所以两个数都对，各自对应一个范围：**
- **1815 = 不含浏览器类的套件**
- **2113 + 2 跳过 = 全部**

**而 `--skip-tests` 那次让 METRICS.md 写了「本次未运行 —— 这不等于通过」。**
**按 §2.6 那条（「没跑成」≠「通过」）这个写法本身是对的，但它让 METRICS.md 暂时不能引用。**
**这一轮末尾重跑了完整 metrics，METRICS.md L13 回到 `1815 通过 / 0 失败`。**
"""

if "恢复变成一条命令" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R912 appended")

VERDICT = """

---

## 第 912 轮：恢复变成一条命令；两个套件数核清了

### `snapshot.py` 加了两个模式

```
python tools/snapshot.py --list                     列出所有快照
python tools/snapshot.py --restore <stamp> [rel]    恢复一个文件或整份
```

| 情形 | 结果 |
|---|---|
| `--list` | 41 份 / 11,770 文件 / 109.5 MB，**并打印实际目录** |
| 不存在的文件 | `not in that snapshot` + `restored 0` |
| 越界路径 | 拒绝，`restored 0` |
| 真实文件 | `restored 1`，虚步骤仍 **175** |

> **`--list` 打印真实路径 `tools/.snapshots` 是刻意的：
> R911 我不是不知道怎么恢复，是**记错了目录名**。所以让命令自己说路径。**

### 一处我该说清的

**`..\\..\\outside.cs` 报的是 `not in that snapshot`，不是我的路径守卫 ——
因为那个文件在快照里不存在，先被存在性检查拒了。**

> **所以路径守卫**只对「快照里存在、但会写到树外」生效**，而快照里不会有那种路径。
> **它现在不验证任何东西。** 留着是因为快照内容将来可能变，但这一点必须写出来。**

### 两个套件数

| 命令 | 结果 | 范围 |
|---|---|---|
| `metrics_report.py` | **1815 通过 / 0 失败** | **不含六个浏览器类** |
| 直接全量 | **2113 通过 / 2 跳过** | 全部 |

**差 298 = R493 排除的六个依赖真 Chrome 的类**（2026-11-14 跑全量耗尽内存导致系统重启之后立的规矩）。

**两个数都对，各自对应一个范围。而 `--skip-tests` 那次让 METRICS.md 写了「未运行 —— 这不等于通过」，
这一轮末尾重跑完整 metrics，L13 回到 `1815 通过 / 0 失败`。**

### 教训

> **R911 我说「记错一个目录名就等于没有快照」。这一轮把它做成命令，并且让命令**自己打印路径**。**
> **而同一轮里我发现：我加的一个安全检查实际上不可达。**
> **「加了检查」和「检查在验证东西」是两件事 —— 而前者会让人以为后者也成立。**
"""

BACKLOG_ADD = """

## 方法 — `snapshot.py` 加 `--list` / `--restore`（R912）

### 起因

**R911 删坏 `StoreFlow.cs` 后按 `tools/.snapshot-backup` 找恢复源，而真实路径是 `tools/.snapshots`
→ 改用 `git checkout` 恢复。**记错一个目录名就等于没有快照。**

### 两个模式

```
python tools/snapshot.py --list
python tools/snapshot.py --restore <stamp> [relpath]
```

| 情形 | 结果 |
|---|---|
| `--list` | 41 份 / 11,770 文件 / 109.5 MB + **打印实际目录** |
| 不存在文件 | `restored 0`，不写 |
| 越界路径 | `restored 0` |
| 真实文件 | `restored 1`，虚步骤仍 175 |

### 一处不可达的检查（必须写明）

**越界拒绝实际由「文件不在快照里」触发，而非路径守卫。
守卫只对「快照里有、但写到树外」生效 —— 而快照来自 `os.walk(src)`，不会有那种路径。
→ **留着但**现在不验证任何东西**。**

### 两个套件数（核清）

| 命令 | 结果 | 范围 |
|---|---|---|
| `metrics_report.py` | **1815 通过 / 0 失败** | 不含六个浏览器类（R493 排除） |
| 直接全量 | **2113 通过 / 2 跳过** | 全部 |

**差 298 = `VoiceListTests` · `GlobalSurfaceTests` · `KeyOrderDispatchTests` · `PatchJournalTests` ·
`PruneWhitelistTests` · `NetworkRecorderLiveTests`。**

| 仍 Unknown | |
|---|---|
| 41 份快照要不要清理 | 109.5 MB，未定策略 |
| 六个浏览器类最近跑过吗 | 未查 |

**纪律**：**「加了检查」和「检查在验证东西」是两件事 —— 前者会让人以为后者也成立。**
"""

BLOCKER = """

---

## 336. 恢复成为命令；两套件数核清（1815 vs 2113）

> R912。**改 `tools/snapshot.py`。**

### 一、两个新模式

```
python tools/snapshot.py --list
python tools/snapshot.py --restore <stamp> [relpath]
```

| 情形 | 结果 |
|---|---|
| `--list` | 41 份 / 11,770 文件 / 109.5 MB + **打印实际目录** |
| 不存在文件 | `restored 0` |
| 越界路径 | `restored 0` |
| 真实文件 | `restored 1`；虚步骤仍 175 |

**`--list` 打印真实路径是刻意的：R911 我不是不会恢复，是记错了目录名。**

### 二、一处不可达的检查

**越界拒绝实际由「文件不在快照里」触发，而非路径守卫。**
**守卫只对「快照里有、但写到树外」生效，而快照来自 `os.walk(src)`，不会有那种路径。**

**→ 留着（快照内容将来可能变），但**它现在不验证任何东西**。**

### 三、两个套件数

| 命令 | 结果 | 范围 |
|---|---|---|
| `metrics_report.py` | **1815 通过 / 0 失败** | 不含六个浏览器类 |
| 直接全量 | **2113 通过 / 2 跳过** | 全部 |

**差 298 = R493 排除的 `VoiceListTests` · `GlobalSurfaceTests` · `KeyOrderDispatchTests` ·
`PatchJournalTests` · `PruneWhitelistTests` · `NetworkRecorderLiveTests`**
（2026-11-14 跑全量耗尽内存致系统重启之后立的规矩）。

**两个数都对，各自对应一个范围。**

### 四、以及一次自己纠正的写法

**中途我用 `--skip-tests` 跑 metrics，METRICS.md 因此写了「本次未运行 —— 这不等于通过」。
按 §2.6 那个写法是对的，但让 METRICS.md 暂时不能引用。末尾重跑完整 metrics → L13 回到 `1815 通过 / 0 失败`。**

### 五、仍然 Unknown

- **41 份快照要不要清理**：**Unknown** —— 109.5 MB，未定策略。
- **那六个浏览器类最近跑过吗**：**Unknown** —— 未查。

### 六、教训

**「加了检查」和「检查在验证东西」是两件事 —— 而前者会让人以为后者也成立。**

**这一轮我加了一个路径守卫，实测两种情形都「拒绝」了，看起来工作正常。
而实际上拒绝来自另一个检查，我的守卫一次都没执行。**

**如果不是我把 `restored 0` 的文案读了一遍，这个守卫会在文档里写成「已验证」。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R912", BLOCKER)
    ensure(RSTATUS, "R912", BLOCKER)
    ensure(RVERDICT, "第 912 轮", VERDICT)
    ensure(BACKLOG, "R912", BACKLOG_ADD)

    note = (
        "\n## R912 补充 — 恢复成为命令；两套件数核清（改 tools/snapshot.py）\n\n"
        "snapshot.py 加 --list / --restore <stamp> [relpath]。四种行为实测：列出（41 份/11770 文件/109.5MB，打印实际目录）· "
        "不存在文件 restored 0 · 越界路径 restored 0 · 真实文件 restored 1（虚步骤仍 175）。\n\n"
        "一处不可达：越界拒绝实际由「文件不在快照里」触发，路径守卫一次没执行 —— 留着但必须写明它现在不验证任何东西。\n\n"
        "两个套件数核清：metrics_report.py 1815（不含六个浏览器类，R493 排除）vs 直接全量 2113 通过 / 2 跳过；差 298 = 那六个类。"
        "两个数都对，各自对应一个范围。\n\n"
        "中途 --skip-tests 让 METRICS.md 写「未运行」→ 末尾重跑完整 metrics，L13 回到 1815 通过 / 0 失败。\n\n"
        "纪律：「加了检查」和「检查在验证东西」是两件事。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R912" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R912"), (RSTATUS, "R912"), (RVERDICT, "第 912 轮"), (BACKLOG, "R912")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R912: recovery becomes a command, and the two suite figures are reconciled\n\n"
         "R911 deleted six thousand characters of StoreFlow.cs and then could not find the snapshot, because the\n"
         " directory name had been remembered as tools/.snapshot-backup when it is tools/.snapshots. Git checkout\n"
         " recovered it, which worked and was luck: the damage was uncommitted, and a commit in between would have made\n"
         " git useless as well.\n\n"
         "So snapshot.py gains --list and --restore. Four behaviours were exercised: listing prints the forty-one\n"
         " snapshots and, deliberately, the directory it actually uses; restoring a name that is not in the snapshot\n"
         " writes nothing; restoring a path that climbs out of the tree writes nothing; and restoring a real file leaves\n"
         " StoreFlow at 175 virtuals.\n\n"
         "One honest note about the guard. The out-of-tree case was refused by the existence check, not by the path\n"
         " guard, because the file is not in the snapshot. So the guard only fires for a snapshot holding a path that\n"
         " would escape -- and snapshots are built from os.walk over src, which cannot produce one. It is kept in case\n"
         " snapshot contents change, but it currently verifies nothing, and saying otherwise would be wrong.\n\n"
         "The two suite figures are now reconciled rather than assumed. metrics_report reports 1815 while a direct run\n"
         " gives 2113 passed and 2 skipped; the difference of 298 is the six browser-dependent classes R493 excluded\n"
         " after a full run exhausted memory and restarted the machine on 2026-11-14. Both figures are right for their\n"
         " scope.\n\n"
         "A wrinkle of my own: running metrics with --skip-tests made METRICS.md say the suite had not run, which is the\n"
         " correct thing for it to say under section 2.6 and made the file unusable for citation. A full run at the end\n"
         " put line 13 back to 1815 passed.\n\n"
         "Unknown: whether the forty-one snapshots should be pruned, now 109.5 MB with no policy; and whether the six\n"
         " browser classes have been run recently, which was not checked.\n\n"
         "The lesson is that adding a check and having a check verify something are different, and the first makes it\n"
         " easy to believe the second. Both cases printed a refusal, and only reading which refusal it was showed that\n"
         " my guard never ran.\n\n"
         "Tool changed; suite green at 1815."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()