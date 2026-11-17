"""Record R1047 as INCOMPLETE: the generator works, the suite was not run. No build, no test.

YG stopped the round because memory was exhausted and a restart is coming. AGENTS 2.6 says a thing not run is neither a
pass nor a failure and must be recorded separately -- so this writes the round up as partial, with the exact resume
point, and touches no build.
"""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")

NOTE = """

## R1047 —— **未完成（内存耗尽，YG 要求重启）** · 生成器已修好，套件**未跑**

> **状态：partial。** 生成器可用、表已生成、`git` 待提交。**全量套件没有跑完** ——
> AGENTS §2.6：「没跑成」既不等于通过也不等于失败，所以这一轮**不能**记成绿。

### 做了什么

1. **取证**：原版在**进度文案**里点名自己解什么 —— `Solving <X>` 族 **36** 条（前缀查询），
   那就是 (f) 要的风控清单，从二进制取到了：

   ```
   Solving Akamai ( · (SBSD) · (SDS)        Solving PerimeterX
   Solving BotDeflector icons · proof of work    Solving Vercel
   Solving Cloudflare ( ×9 阶段               Solving Stripe challenge
   Solving DataDome (I)                      Solving PayPal 3DS (1)…(8)
   Error Solving Queue-it (Softblock)        Solving captcha ( · challenge (S) · checkpoint · POW
   ```

2. **新生成器** `replica/tools/vendor_coverage.py` → `replica/docs/VENDOR_COVERAGE.md`，
   每次运行重探 13 个厂商 + 2 个对照（`kpsdk` 17 · `datadome` 15），并对账 `VendorWiring` 的 **7** 行。

3. **结果**：`controls ok=True · vendors named=13 · wiring rows=7 · missing=7`

   | 缺的 | 命中 | 性质 |
   |---|---|---|
   | `BotDeflector` | 2 | **真厂商缺口** |
   | `Vercel` | 2 | **真厂商缺口** |
   | `Stripe challenge` | 1 | **真缺口（支付挑战）** |
   | `PayPal 3DS` | 9 | **真缺口（支付挑战）** |
   | `captcha` | 1 | 挑战类型，`VendorWiring` 形状不建模 |
   | `proof of work` | 1 | 同上 |
   | `checkpoint` | 1 | 同上 |

   **→ 所以 7 个里 4 个是真缺口，3 个是形状不匹配。**

### 而我这一轮踩了一个坑（已修，但值得记）

**第一版解析器找 `Vendor.X`，而真实形状是 `new Row("cloudflare", ...)` 小写字符串 ⇒ 解析到 0 行，
于是把 13 个厂商**全**报成「缺」。**
→ **那是 R764 那个形状的又一次：解析器错 ⇒ 结论假，而且假得很有说服力。**
→ 修法：按 `new Row(` 切块，每块解析 `State.X` / `Solver.Y` / 尾随 bool；
**并加了一条 `rows == 0` 就拒绝出表**的保护（`return 2`），因为空解析不该产出任何清单。

**第二个坑**：我用 `Set-Content` 无编码写回，把 UTF-8 文件写成了 GBK ⇒ `SyntaxError: Non-UTF-8`。
→ 已用 `write` 工具整份重写。**教训：不拿 PowerShell 对源码做文本手术。**

### 数字

| 度量 | R1046 | **R1047** |
|---|---|---|
| 套件 | 2258 / 0 | **未跑 —— 内存耗尽，重启前不跑** |
| 函数数 | 174,293 | **未重测** |
| 产物陈旧度 | 0 / 0 | **未重测**（本轮只加了 tools/ 与 docs/） |
| **`Solving` 族前缀命中** | 未查 | **36** |
| **原版点名的求解对象** | 未知 | **13** |
| **`VendorWiring` 行数** | 7（记录） | **7（已解析验证）** |
| **真厂商缺口** | 未知 | **4**（BotDeflector · Vercel · Stripe challenge · PayPal 3DS） |
| **形状不匹配的 3 个** | — | captcha · proof of work · checkpoint |
| **对照** | — | **成立（17 / 15）** |
| **`docs/VENDOR_COVERAGE.md`** | 不存在 | **已生成（UTF-8）** |

### 重启后第一步

```
cd D:\\projects\\cyber-reverse\\replica
python tools\\vendor_coverage.py          # 确认 rows=7 · missing=7
python tools\\metrics_report.py           # 跑全量，确认套件仍 2258/0/0
```

**→ 若套件绿，则 R1047 收尾；若不绿，按红的守卫改数字或回滚。**
**→ 然后按 (f) 给那 4 个真缺口逐条写「为什么未覆盖」—— 而 `BotDeflector` 是 R1022 就记过的第二个 flow 候选。**

### 纪律

**内存不足时先停构建。** 而「未跑」要写「未跑」，不能因为「上次是绿的」就当作绿。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1047", NOTE)
append(RBLOCK, "R1047", "\n---\n\n## 471. **R1047 未完成（内存耗尽）· 生成器已修好 · 套件未跑**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1047 (partial): the original names thirteen solvers; the suite was not run\n\n"
     "Recording this round as partial. YG stopped it because memory was exhausted and a restart is coming, so nothing\n"
     " here was built or tested, and per AGENTS 2.6 an unrun suite is neither a pass nor a failure.\n\n"
     "What did land: the original's own account of what it solves. Its user-facing progress text carries a Solving\n"
     " family of thirty-six strings naming Akamai with two variants, Cloudflare across nine stages, DataDome,\n"
     " PerimeterX, Vercel, BotDeflector, Queue-it in an error line, Stripe and PayPal 3DS, plus captcha, proof of work\n"
     " and checkpoint. That is the vendor inventory criterion (f) asks for, taken from the binary rather than from our\n"
     " own classification, and it exists even though R1045 showed the artifact has no symbols, because this is data.\n\n"
     "A new generator reconciles it against VendorWiring's seven rows with two controls, kpsdk at seventeen and\n"
     " datadome at fifteen. Seven things the image names have no row: BotDeflector, Vercel, Stripe and PayPal 3DS are\n"
     " real gaps; captcha, proof of work and checkpoint are challenge types the row shape does not model.\n\n"
     "Two mistakes this round worth carrying forward. My first parser looked for Vendor.X and the real shape is a\n"
     " lowercase string in a constructor call, so it parsed nothing and reported all thirteen vendors as missing -- a\n"
     " wrong parser producing a confident false inventory, which is R764 again, and it now refuses to publish when it\n"
     " parses zero rows. And I rewrote a source file with Set-Content and no encoding, turning UTF-8 into GBK; the file\n"
     " is rewritten properly and the lesson is not to do text surgery on source with the shell.\n\n"
     "Figures: the suite is unrun, the function count and freshness are unremeasured because they need a build, and the\n"
     " measurements that did happen need none -- thirty-six Solving strings, thirteen named solvers, seven wiring rows,\n"
     " four real gaps, controls at seventeen and fifteen.\n\n"
     "Resume: regenerate the table, then run the full suite and record whether it is still green.\n\n"
     "The discipline that matters here is that not-run has to be written as not-run, and a previous green does not\n"
     "lend itself to this round."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
