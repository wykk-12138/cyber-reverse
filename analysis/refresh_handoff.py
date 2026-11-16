"""Refresh HANDOFF.md to the state at R826 and commit. (R826)

YG asked for the progress to be saved again. Everything is already committed; what has aged is the handoff, which was
last rewritten at R823 and has since gained R824, R825 and R826. This rewrites the top of it so a new session reads the
current state first rather than four rounds of history.

Position of the file is preserved: the older sections stay, the status block at the top is replaced wholesale.
"""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

NEW_TOP = """# 交接（2026-11-16 20:40，R826 后）

## 现在在哪

- **轮次**：R826 已提交（`git log` 顶端应为 `drop the record helper` / `R826: NikeFlow reads structurally…`）。
- **内存**：1.91 GB / 31.71 GB。**低于 2 GB ⇒ 只用 `-m:1`，不跑全量。** 低于 1 GB 停构建。
- **套件**：最后一次确认绿是 R823（`DocsConsistencyTests` 7/7）。**R824–R826 未跑全量**（内存纪律）。
  重启或内存回到 2 GB 以上后先跑一次 `python tools\\metrics_report.py`，**期望 1766 / 0**。
- **四项度量**（沿用 R820）：名字级 `real gap 4 / missing 16` · 类型级 `0` · 类型缺失 `17` · 形状 `78` · 文案 `0`。

## 完成判据现状

| 判据 | 状态 |
|---|---|
| (a) 类型级缺口 / 类型缺失 | **已分类完毕**：见 `docs/TYPE_PRESENCE_TRIAGE.md`（2 越界 · 7 改名 · 1 结构性 · 7 契约无判别力） |
| (b) 文案 | **0**，无剩余 |
| (c) 产物级对照 | **PASS** —— `python analysis\\verify_artifact.py`：1142/1142 locale · 20/20 资源 · 12/12 叶子 |
| (d) claim 表 | **PASS 规则** —— `python analysis\\check_claims.py`：5 行，2 pass / 3 fail，全有 authority |
| (e) 套件 / 变异 / 数字来源 | **待一次全量确认**（内存所限未跑）；数字全部出自 `docs/METRICS.md` |
| (f) 核心覆盖表 | 风控已对账（R807）；站点复刻件→镜像已逐条（49/57 有据 · 6 零 · 2 仅噪音）；**镜像→复刻件未分类** |

## 未结案项（按价值排序）

1. **两个真死步骤（R824）**：`HandleResponseAsync` 与 `RefreshSessionAsync`，**总提及都是 1**（只有自己的声明）。
   `StoreFlowParityTests` 的规范步骤表含 `RefreshSession`/`VerifySession` → **镜像有这些阶段**。
   **下一步：读反编译，看 `RefreshSession` 挂在哪个时刻。猜一个调用点 = 假覆盖（R799）。**
2. **长度守卫（R826）**：`ScheelsFlow`（`body.Length > 200`）与 `BstnFlow`（`> 2000`）把「响应体短/空」也判成
   `available=false`。**误报缺货 = 错过 drop，不可重来**，而它由与商品无关的量决定。
   两种改法（明确失败 / 先看 `lastStatus` 判 `Blocked`）**都需要镜像证据**。
3. **8 个未通读的可用性解析**（通读 12/20）：`Hbx` `Hybris` `Magento` `JohnLewis` `PopMart` `YeezySupply`
   `Casio` `Shopify`。**其中还有几个用长度守卫？Unknown —— `BstnFlow` 是偶然撞见的。**
4. **3 个忽略 `c.Url` 的流程**（`NikeFlow` / `PoqAppFlow` / `SuperswipeFlow`，与 `ModuleRobustnessTests`
   例外名单一致）：**待判「忽略是对的还是遗漏」，判据在镜像里。** 工具：`analysis\\scan_url_ignoring4.py`。
5. **镜像→复刻件方向**：池子有 1182 个 `myshopify` 主机（**下界**），复刻件 33 个别名覆盖 30。
   **未分类，成因写的是「未逐个取证」。**

## 工具的可信边界（这一条最省时间）

- **`analysis/pe_strings.txt` 是抽样**（180,228 行 vs 镜像 324,895 条串）。**正向可用、反向不可用** ——
  反向结论用 `python analysis\\ida.py str <pat>`。见 `AGENTS.md` §2.7b。
- **`ida.py str` 默认 `limit 40`**（已加 `--limit`），**插件侧还有约 500 条上限**。数数要写明是下界。
- **判断「某方法是否被调用」不要用调用图扫描**：委派是**无接收者**调用（`=> FindProductAsync(c, ct)`），
  `\\w+\\.名字` 一定漏。**用「裸名字总提及次数 = 1 ⇒ 只有声明 ⇒ 真死」这个判据。**（R824 两次扫描都错在这）
- **按花括号或「最近前缀 class」定类边界都会错**（一文件多类 + 字符串里的 `{`）。
  **可用做法**：缩进切类 + 截到下一个成员声明（`scan_url_ignoring4.py`）。
- **文档守卫**：`DocsConsistencyTests` 扫 `replica/docs/VERDICT.md` 正文里所有「数字 + 个模块 / modules」，
  要求全等于 63。**写记录时别把违规字符串抄进去** —— 引号复述等于又写一遍（这个坑踩过三次）。
- **`Get-Content -Raw` 读 1.9 MB 的 `VERDICT.md` 会把中文比错**。判断文件内容**只看字节**
  （`io.open(p, 'rb')` + `decode('utf-8')`）。

## 机器相关

**内存不足导致重启过一次。** 重启后若 `available < 2GB` 只用 `-m:1`；`< 1GB` 停构建。
**IDA 若需重开**：后台跑 `powershell -File "D:\\projects\\vm2api\\.dsh\\scripts\\ida-mcp-doctor.ps1" -Path <目标.i64>`，
同时用 CUA 轮询点掉「请确认」类对话框，**判据是「再读一次没有框」**。
**IDA 未开时不要硬做需要反编译的事** —— 本轮次两次因此挂起（R824、R826 的镜像侧问题）。
"""


def main():
    old = io.open(HANDOFF, encoding="utf-8").read()
    # keep everything from the first "## " section that starts with 下一步 or 完成判据 onward, if present
    marker = "## 下一步该做的"
    tail = ""
    if marker in old:
        tail = "\n---\n\n# 历史（R823 时的交接原文，保留）\n\n" + old[old.index(marker):]
    elif "## 重启后第一件事" in old:
        tail = "\n---\n\n# 历史（R823 时的交接原文，保留）\n\n" + old[old.index("## 重启后第一件事"):]

    io.open(HANDOFF, "w", encoding="utf-8", newline="").write(NEW_TOP + tail)
    print("  handoff rewritten: %d chars" % len(NEW_TOP + tail))

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "Refresh the handoff to the R826 state\n\n"
         "The handoff was last written at R823 and three rounds have landed since. The top now states where the suite"
         " stands and that R824 to R826 did not run it under the memory discipline, lists the five open items in value"
         " order, and collects the tool boundaries that cost the most time to learn: the string pool is a sample so it"
         " answers positives only; ida.py str has a forty-result cap and the plugin a five-hundred one, so any count is"
         " a bound; a call-graph scan cannot prove a method unused because delegation is an unqualified call, and the"
         " bare-name-mention count is the criterion that works; class boundaries cannot come from brace matching or"
         " from the nearest preceding declaration; and the doc guard rejects any number other than the catalogue count"
         " in prose, so a record must describe a bad string rather than quote it.\n\n"
         "The earlier sections are kept below a history heading rather than discarded."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
