# 交接：卡点与阅读路线

> **这份文档不搬内容，只给路线。**
> 每条卡点后面写的是「按顺序读哪几份文档的哪一节、为什么那里有你需要的东西」。
> 证据、数字、论证全在那些文档里，**不要另立一份摘要**——那样只会多一个会过期的副本。

---

## 0. 一句话现状

原版 `target\Cybersole.exe`（.NET 10 NativeAOT，无 IL）→ 复刻件 `replica\`（.NET 8 + Avalonia）。
**四项度量**：名字级 real gap 4 / 类型级 0 / 类型缺失 17 / 形状差异 80；**完整套件 1619 通过 0 失败**。
**判据 (c)(d)(e) 满足；(a)(b) 未满足 → 目标未达成。**
（数字只从 `docs/METRICS.md` 读，那是 `python tools/metrics_report.py` 生成的。）

---

## 1. 卡点一：(a) 的 `LicenseControl.Authenticate`

### 事实

`Authenticate` 在 `replica/src/` **全库 0 次出现**。这是**真缺**（能做而没做），
不是判据 (a) 括号里允许的「不可得」。其余 16 条类型缺失都已逐条定性。

### 阅读路线（按顺序，别跳）

| # | 读什么 | 为什么 |
|---|---|---|
| 1 | `docs/COMPLETION_AUDIT.md` §(a) | 终审怎么下的这个判断，以及为什么其余 16 条合规 |
| 2 | `docs/TYPE_PRESENCE_TRIAGE.md` | 17 条的逐条判定与证据（7 改名 / 1 结构差异 / 1 真缺 / 8 Unknown） |
| 3 | `docs/BLOCKERS.md` **§118** | 判据第三版「同一类体内共现」；以及为什么前两版各错一个案例 |
| 4 | `docs/BLOCKERS.md` **§124** | **最重要**：5 种探针证明「字符串 → xref」在这个二进制上天然为空（0 引用、0 指针、`trace_data_flow` depth=0） |
| 5 | `docs/BLOCKERS.md` **§35** | **反面但可用**：绕开字符串的入口确实存在 —— **导入 thunk → 调用点 → 反编译**。这是目前唯一被验证过的定位法，但只对"走 Win32 API 的代码"有效 |
| 6 | `docs/APP_LAYER_BOUNDARY.md` | 七条「哪些函数属于应用层」的路线全部被否；写清了还缺什么才能解锁 |

### 这张牌桌的实情

- **311,203 / 321,244 个函数无名**（`python analysis/ida.py survey` 可复算）
- 字符串无 xref，数据表无指针 → 常规「字符串 → 交叉引用 → 函数」不通
- **但** `§35` 的 thunk 路线通；问题是 `Authenticate` 未必走 thunk
- `.pdata` 有 277,094 条展开记录可作函数清单，按大小/调用图筛是可行但昂贵的路

---

## 2. 卡点二：(b) 的判据口径 —— **等 YG，不能自行决定**

### 事实

判据 (b) 原文假设「剩余文案是字符串池中截断」。**实测前提为假**：

| 事实 | 读哪 |
|---|---|
| 两条文案在池里完整、占位符齐全；裸键名单独存在（原版按 key 查表） | `BLOCKERS.md` **§27**、**§101** |
| 四种语言（en/ja/zh/ko）译文都在 | `BLOCKERS.md` **§102** |
| 校验所需名单**也在**：英语 `state` 50 条 + `state_abbr` 50 条 + 国名 244 条 | `BLOCKERS.md` **§121** |
| **缺的是规则**：何时校验 / 大小写 / 是否接受缩写 / 按国家还是按 locale | `BLOCKERS.md` **§121**、`docs/FAKE_DATA_BOUNDARY.md` §二 |
| 三条处置路径与各自代价/风险 | **`docs/CRITERION_B_OPTIONS.md`** ← 决策就在这份里 |

### 为什么我不自己选

判据是**考题**。改它的口径 = 改考题。`CRITERION_B_OPTIONS.md` 把 A（改口径）/ B（实现校验）/ C（保现状等证据）/ D（拿规则）四条路的代价都列了，**摆事实，不选**。

---

## 3. 别重走的路（已否证，读结论即可）

| 路线 | 在哪被否 |
|---|---|
| ~~字符串 → xref → 函数~~ **（R703 已撤回，这条路是通的）** | ~~`§32`、`§34`、`§124`~~ —— 见 `§134`：**引用一直在，我探的是字符地址，代码 `lea` 的是对象头（差 12 字节）**。用 `analysis/xref_both.py` 同时试两个地址 |
| 递归展开 / unwind info / 继承链 判应用层 | `§36`、`§78`、`§42` |
| 可达性 BFS / 函数指针表桥 | `§50`、`§51` |
| 三条候选重分类去解那 8 条 UNKNOWN | `§88` |
| 用 Ghidra 当第三个权威 | `§3`（`PARITY_CLAIMS.md` §0 有完整拒绝理由） |
| `pe_strings.txt` 找文案 | `§101` —— 它是**纯 ASCII**，CJK 全丢；要用 `pe_strings_utf8.txt` |

**`BLOCKERS.md` §6「已有否证的不可得项（不要再花时间）」是这张表的权威版**，动手前先读它。

---

## 4. 假数据那条线：**数据全可得，行为全 Unknown**

这是本 session 里最深的一条链（R670–R688），**格式已完全解出并被 ISO 外部验证**。
要接手先读 **`docs/FAKE_DATA_BOUNDARY.md`**（一页纸，含格式规格 + 最小行为证据清单 + 解锁条件）。

关键：**数据侧结案，行为侧一条都没解开**。别再去找数据。

---

## 5. 工具与可复算命令

```powershell
# 在 replica\ 下
python tools\metrics_report.py               # 四项度量 + 完整套件（自带内存守卫）
python tools\metrics_report.py --skip-tests  # 只要度量，~2 s
python tools\shape_audit.py                  # 形状差异明细
python tools\aot_member_coverage.py          # C10：产物里成员可见性（当前 12/819）
python tools\datafiles_diff.py               # 持久化文件名对照（读 %APPDATA% 只列不写）

# 在根目录
python analysis\type_presence_triage.py      # 17 条逐条判定
python analysis\audit_claims.py              # claim 表 vs METRICS（应为 0 处不一致）
python analysis\iso_diff.py                  # 国家码 vs ISO（应 PASS）

# IDA（两个实例：原版 13337 / 复刻件 13338）
python analysis\ida.py health                # 就绪判定
python analysis\wait_ready.py 13338 1500     # 等 auto_analysis_ready，别用端口判断
python analysis\func_compare.py --export-only # 导出函数清单（已内置就绪门 + 口径头行）
python analysis\run_idapy.py <snippet.py>    # 跑 IDAPython（片段走文件，避开 shell 转义）
```

**IDA 启动要过三个模态框** —— `docs/IDA_STARTUP_CHECKLIST.md` 有完整清单，**别跳**。

---

## 6. 红线（违反即结论作废）

1. **`%APPDATA%\Cybersole` 与 `%LOCALAPPDATA%\Cybersole` 只读**。可以列目录、读文件，**绝不写入**。
2. **复刻件自己写出的** `settings/tasks/solvers/checkoutHistory` **不得当实机证据**（循环论证）。
3. **数字只来自 `docs/METRICS.md`**。任何文档不得硬编码四项度量。
4. **判据 (a)–(e) 是考题**，改口径要 YG 点头。
5. **Observation 只能来自工具引用的证据**；推理标 Inference + 置信度 + 备择；覆盖不全/能力不支持/证据冲突一律显式 **Unknown** 并写缺什么。
6. **结构对等 ≠ 行为对等**：只能证明属性存在的成员，行为必须记 Unknown。
7. 当前有一条**已知未修的历史破坏**：R690 的全局替换把三份记录里 21 处「反斜杠+反引号」删了，
   含合法的 C# 泛型元数转义。**已记为已知缺陷，不擅自动历史**（git 从 R691 起才有）。

---

## 7. 给头脑风暴的六个问题

不是要你回答全部，是给你起手的位置：

1. **(a) 的 `Authenticate`**：在「字符串无 xref + 311k 无名函数」这个前提下，
   除了 `§35` 的 thunk 路线和 `.pdata` 全筛，还有**第三种**定位法吗？
   （提示：想想 NativeAOT 还留下什么结构 —— `MethodTable`、vtable slot、`.pdata` unwind、导入表、
   还有 `§79`–`§82` 里那些已量的分派表。）
2. **(b) 的口径**：如果 (b) 的前提本来就写错了，改判据的**最小**改动是什么？
   有没有一种改法，既能容纳"数据齐、规则缺"，又不至于让任何有解释的缺口都算过？
3. **函数数量对等**：`321,244 ↔ 186,732`（同口径）比值 0.581。
   在"差的一半落在 ≤32 B 胶水函数"这个已知事实下，**这个比值还能怎么读**？
   （`§47`/`§48`/`§49` 有全部数据，`§49` 还写了肉眼抽样为什么不够。）
4. **效率相近**：这条**从未验证**（`§4`）。有没有一种不依赖登录凭据的代理指标，
   比现有的「零直接 xref 比例」更接近"效率"？
5. **C10 = 12/819**：807 个成员在产物里不可见。这是**裁剪**、**内联**，还是**只在元数据里**？
   有没有办法把这三者分开？（`§126`/`§127` 有测量条件，`§132` 有符号口径头行。）
6. **方法本身**：本 session 里同一个坑踩过 3 次（分析中途截断，`§43`/`§44`/`§127`，比值都是 0.730）。
   `docs/TRAP_ENTRY_CLOSURE.md` 把 123 条坑按「有没有操作入口」清了一遍。
   **还有哪些"教训写在报告里、犯错发生在操作里"的缺口？**

---

## 8. 接手第一步

```powershell
cd D:\projects\cyber-reverse
git log --oneline -5              # 看最近做了什么
git status --short                # 应为空
python replica\tools\metrics_report.py --skip-tests   # 确认度量与 METRICS.md 一致
```

然后读 `docs/COMPLETION_AUDIT.md`（一页纸，终审表），再按上面的路线走。
