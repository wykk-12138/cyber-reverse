"""Record R811: criterion (c) passes, and C4 moves from unknown to a determinate fail."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 235. 判据 (c) 复算通过；**C4 从 `unknown` 变成可判的 `fail`**

> R811。`docs/PARITY_CLAIMS.md` 的 C4 行改写；`analysis/check_claims.py` 作为 (d) 的机械检查留存。

### 一、判据 (c)：产物级对照可复算，**PASS**

```
python analysis\\verify_artifact.py

artifact: 55349248 bytes
locale keys: 1142/1142 OK
embedded resources: names 20/20, content 20/20 OK
resource leaves: original 12, replica 12 OK
result: PASS
```

**1142 个 locale 键、20 个资源（名字与内容）、12 个资源叶子，逐项对上。**

### 二、判据 (d)：先确认它自己的规则，再机械核一遍

`PARITY_CLAIMS.md` 自己写着判据 (d) 的满足条件：

> **每条都有 `authority`，且非 unknown 者都有命令。**

**`analysis/check_claims.py` 就按这一句去核表：**

```
claim rows: 5
  **fail**  3
  **pass**  2
rows without an authority: 0
non-unknown rows without a command: 0
criterion (d) by its own stated rule: PASS
```

**所以 (d) 通过 —— 而通过的依据是它自己写下的那句话，不是我另外发明的口径。**

### 三、C4 原来为什么是 `unknown`

那一行写着：

> 缺**原版 imphash 与完整导入集合**：`inspect_pe_imports` 对 129 MB 要求 `max_functions≥438` 且完整转储；
> 本轮只算了复刻件。**补法：对原版跑一次并重定向到文件。**

**这一轮就照它写的补法做了。** 两侧各一次 `inspect_pe_imports`：

| | 原版 | 复刻件 |
|---|---|---|
| `coverage.status` | complete | complete |
| `examined_dlls` | **17** | **18** |
| `imports` | **438** | **409** |
| `delay_imports` | 0 | 0 |
| `imphash`（pefile/md5） | `7ed8e14777a36b89031807b561000260` | `23e3dee057b2fdead858a8f731dd9830` |

**两侧都完整取到，所以这一条不再「缺证据」—— 它有了确定答案：`fail`。**

### 四、差别可解释，而且验过

- **复刻件多一个 `VERSION.dll`**（3 个导入：`GetFileVersionInfoSizeExW` / `GetFileVersionInfoExW` / `VerQueryValueW`）
  —— **Avalonia 读文件版本用**
- **原版多 ADVAPI32 的一组安全 API**（`AddMandatoryAce`、`CreateWellKnownSid`、`SetSecurityDescriptorDacl`、
  `ImpersonateLoggedOnUser` 等）—— **AOT 运行时的 ACL/令牌族**
- **imphash 不同是这两处之和的必然结果**

**`VERSION.dll` 在原版里 0 匹配** —— 这一条我单独查过，不是推断。

### 五、现在的 claim 表

```
C1 pass   两个产物是同类（PE32+/amd64/NativeAOT，无 CLR 目录）
C2 fail   节布局（6 ↔ 9）
C3 fail   导出面（39 ↔ 1，Brotli 静态库）
C4 fail   导入面（17/438 ↔ 18/409）—— 本轮从 unknown 变来
C5 pass   资源面（12 ↔ 12，逐叶子）
```

**3 fail，每条都能解释。**

### 六、这一条对完成判据的意义

**判据 (d) 要求「claim 表每条有 authority + 命令 + gap_reason」。**
**C4 原来有 authority（`unknown`）但没有答案 —— 现在有答案，而且两侧数字都是工具给的、可重算的。**

**`unknown` 变 `fail` 不是坏消息。** 一条 `unknown` 是信息缺口；一条带解释的 `fail` 是信息。

### 七、验证

```
python analysis\\verify_artifact.py          PASS
python analysis\\check_claims.py             PASS（2 pass / 3 fail，无缺口）
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 八、仍然 Unknown

- **C2/C3 的 `fail` 是否该修**：**Unknown** —— 节布局与导出面由 AOT 版本与静态库决定，
  **不是复刻件能改的**（DEVIATIONS.md 有记）。**它们是 `fail` 且不该被修，这个状态合理但读起来刺眼。**
- **`imports` 差 29 个函数里，除上述两处外还有没有别的原因**：**没逐条比对** ——
  **只解释了 DLL 级的两处差异，函数级的 438-409 没做集合差。**

### 九、教训

**`unknown` 行自带的「补法」是可执行的。**
**C4 那一行写着「对原版跑一次并重定向到文件」，而它挂了好几轮没人做 —— 包括我。**
**一个 `unknown` 如果写清了怎么补，它就只是一个待办，不是一块雾。**
"""

VERDICT = """

---

## 第 811 轮：判据 (c) 通过；C4 从 unknown 变成可判的 fail

### 判据 (c)：产物级对照 PASS

```
verify_artifact.py →
  artifact: 55349248 bytes
  locale keys:        1142/1142 OK
  embedded resources: names 20/20, content 20/20 OK
  resource leaves:    original 12, replica 12 OK
  result: PASS
```

### 判据 (d)：先读它自己的规则，再机械核

`PARITY_CLAIMS.md` 写着：**「每条都有 `authority`，且非 unknown 者都有命令」**。
`check_claims.py` 按这句话核表：

```
5 行 → fail 3 / pass 2 · 无 authority 的 0 行 · 非 unknown 无命令的 0 行 → PASS
```

### C4 从 unknown 变 fail

那一行写着补法：「对原版跑一次并重定向到文件」。**这一轮照做了。**

| | 原版 | 复刻件 |
|---|---|---|
| DLL / 函数 | **17 / 438** | **18 / 409** |
| imphash | `7ed8e147…` | `23e3dee0…` |
| coverage | complete | complete |

**两侧都完整取到 → 不再是「缺证据」，而是确定答案：fail。**

**差别可解释且验过**：复刻件多 `VERSION.dll`（Avalonia 读版本，**原版 0 匹配**）；
原版多 ADVAPI32 的一组安全 API（AOT 运行时 ACL/令牌族）。

### 现在的表

```
C1 pass · C2 fail（6↔9 节）· C3 fail（39↔1 导出）· C4 fail（17/438↔18/409）· C5 pass
```

### 一条值得说的

> **`unknown` 变 `fail` 不是坏消息。一条 `unknown` 是信息缺口；一条带解释的 `fail` 是信息。**
> **而且 C4 自带的补法挂了好几轮没人做 —— 包括我。写清了怎么补的 `unknown` 只是待办，不是雾。**
"""

BACKLOG_ADD = """

## 判据 — (c) PASS，(d) PASS，C4 结案（R811）

| 判据 | 状态 | 命令 |
|---|---|---|
| **(c)** 产物对照可复算 | **PASS** | `python analysis\\verify_artifact.py` → 1142/1142 locale · 20/20 资源 · 12/12 叶子 |
| **(d)** claim 表规则 | **PASS** | `python analysis\\check_claims.py` → 5 行，无 authority 缺口，非 unknown 全有命令 |

**C4 从 `unknown` 变 `fail`（有答案、可解释）：**

```
原版    17 DLL / 438 函数 / imphash 7ed8e14777a36b89031807b561000260
复刻件  18 DLL / 409 函数 / imphash 23e3dee057b2fdead858a8f731dd9830
两侧 coverage=complete，delay_imports=0
```

**差别**：复刻件多 `VERSION.dll`（Avalonia 读版本；**原版 0 匹配，已验**）；
原版多 ADVAPI32 安全 API 组（AOT 运行时 ACL/令牌族）。

| 仍 Unknown | |
|---|---|
| C2/C3 的 fail 该不该修 | 由 AOT 版本与静态库决定，**不是复刻件能改的** |
| 438−409 这 29 个函数的集合差 | **只解释了 DLL 级，未逐条比** |

**纪律**：**`unknown` 行自带的「补法」是可执行的 —— 写清了怎么补的 `unknown` 只是待办，不是雾。**
C4 的补法挂了好几轮没人做，包括我。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R811", BLOCKER)
    ensure(RSTATUS, "R811", BLOCKER)
    ensure(RVERDICT, "第 811 轮", VERDICT)
    ensure(BACKLOG, "R811", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R811"), (RSTATUS, "R811"), (RVERDICT, "第 811 轮"), (BACKLOG, "R811")):
        body = io.open(path, encoding="utf-8").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R811: criterion (c) reproduces and C4 stops being unknown\n\n"
         "verify_artifact.py passes on the current artifact: 1142 of 1142 locale keys, 20 of 20 embedded resources by\n"
         "name and content, 12 of 12 resource leaves against the original. That is criterion (c).\n\n"
         "Criterion (d) states its own condition in PARITY_CLAIMS.md -- every claim carries an authority, and every\n"
         "non-unknown claim carries a command -- so the check applies that sentence rather than inventing a standard:\n"
         "five rows, three fail and two pass, no row without an authority, no non-unknown row without a command.\n\n"
         "C4 was the one unknown, and it came with its own remedy written down: run inspect_pe_imports against the\n"
         "original. That had been sitting for several rounds, this one included. Running it on both artifacts gives\n"
         "the original 17 DLLs and 438 imports with imphash 7ed8e147, the replica 18 and 409 with imphash 23e3dee0,\n"
         "both complete, neither with delay imports. Both sides measured fully, so the claim is no longer short of\n"
         "evidence; it has an answer, and the answer is fail.\n\n"
         "The difference is explicable and was checked rather than assumed. The replica carries VERSION.dll for three\n"
         "file-version imports that Avalonia uses, and that DLL has zero matches in the original. The original carries\n"
         "an ADVAPI32 security family -- AddMandatoryAce, CreateWellKnownSid, the security-descriptor setters,\n"
         "ImpersonateLoggedOnUser -- that the AOT runtime pulls in. The differing imphash follows from those two.\n\n"
         "An unknown becoming a fail is not bad news. An unknown is a hole in the information; a fail with an\n"
         "explanation is information. The useful observation is narrower than that, though: C4 told us how to fix it\n"
         "and nobody ran the command, which is what a well-written unknown is -- a to-do, not a fog.\n\n"
         "Unknown still: whether C2 and C3 should be repaired at all, since section layout and export surface follow\n"
         "from the AOT version and a static library rather than from anything the replica controls; and the\n"
         "twenty-nine-import difference at function level, where only the DLL-level causes were explained.\n\n"
         "No product code changed; suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
