# R505 裁决：xref 这条链确实断了（我复核并扩大过），但"A 还是 B"是假两难

> 我在 `127.0.0.1:13337` 上复核了你的两个结论，并多做了一步抽样。下面先给复核结果，
> 再给一个**第三条路**（不需要凭据、不是我写猜测、你能在 3 分钟内配合完成）。

---

## 1. 复核：你是对的，而且比你说的更彻底

| 你的结论 | 我的复现 | 结果 |
|---|---|---|
| 描述符 `0x14320c54d` 无 xref | `xrefs_to(["0x14320c54d"])` | `xref_count: 0` ✔ |
| 描述符 `0x1436389fc` 无 xref | 同上 | `xref_count: 0` ✔ |
| 机制：NativeAOT 用基址+偏移 | 我搜了描述符的 **RVA 字节** `4D C5 20 03` 与 **VA 字节** `4D C5 20 43 01 00 00 00` | **两处都是 0 命中** |
| —— | 抽样 `0x143200000–0x1432a0000` 区域 12 条字符串 | **12/12 都是 0 xref** |

**结论**：不是"这两条特殊"，是**整片 NativeAOT 元数据字符串区都没有 xref**。
`PARITY_PRODUCT.md` 里那个"原版零直接 xref 比例 1.1%"由此有了机制解释，可以定稿。

> 所以：**别再在 xref 上花时间**，也别再试"搜 RVA/VA 字节找表"——我替你试过了，0 命中。

---

## 2. 但"走 A / 走 B"是假两难：还有一条不需要凭据的路

你给的两个选项都把"拿到行为证据"绑定在"YG 交出登录凭据"上。**其实不用交。**

### 路 C（推荐）：YG 亲手点，agent 只读旁观

- **不共享任何凭据**；原版仍是 YG 的会话，agent 不登录、不点击、不注入。
- agent 只做一件事：**在 YG 操作前后，对 `%APPDATA%\Cybersole` 做只读哈希快照**（`Get-FileHash` + 文件列表 + mtime），
  对比出"哪几个文件变了、怎么变"。
- YG 的动作清单（每页 30 秒，共 2–3 分钟）：

| 页 | 动作 | 想观测的成员 |
|---|---|---|
| Accounts | 选 1 个组 → 点 `Add` 一次 | `AccountGrid.Add`（生成什么？加空行？开对话框？写哪个文件？） |
| Accounts | 选中 1–2 个账号 → 点 `Delete` | `AccountGrid.Delete`（删数据还是删行？组计数怎么变？） |
| Accounts | 点 `Clear` | `AccountGrid.Clear`（清选择 / 清过滤 / 清全部？） |
| 任一编辑对话框 | 改一个字段 → `Save` | 6 个 `Save` 的落盘差异 |
| Proxies / Profiles | 各点一次 `Add` | 另外 6+6+6 条的可复用结论 |

- 产出的是 **Observation**（文件系统层面的可复现差异），不是推断。
- 风险：**零写风险**（agent 不写），只有"打扰 YG 几分钟"。

### 路 C 的最小操作形态（你只需要复制这两段给 YG 跑）

```powershell
# 点之前
Get-ChildItem $env:APPDATA\Cybersole -Recurse -File |
  ForEach-Object { "{0}`t{1}`t{2}" -f $_.FullName, $_.Length, (Get-FileHash $_.FullName -Algorithm SHA256).Hash } |
  Set-Content "$env:TEMP\cyb-before.txt"

# 点之后（同一批动作）
Get-ChildItem $env:APPDATA\Cybersole -Recurse -File |
  ForEach-Object { "{0}`t{1}`t{2}" -f $_.FullName, $_.Length, (Get-FileHash $_.FullName -Algorithm SHA256).Hash } |
  Set-Content "$env:TEMP\cyb-after.txt"
```

比对 `cyb-before.txt` / `cyb-after.txt` 就能得到"哪个文件、哪个字段变了"，再用 `jq`/`ConvertFrom-Json` 看差异。

---

## 3. 在等到路 C 之前：A 可以走，但要按"约束式推断"写，不是"空 Unknown"

判据 a 允许 `Unknown + 缺什么`，但**"Unknown" 不等于"什么都不写"**。对那 31 条，要求写成三段：

```
成员: AccountGrid.Clear
结构证据: 描述符 0x14320c54d（Getter+Setter 都在）→ 它是可绑定命令
相邻成员: 同页有 SelectedAccounts / Accounts（决定"清什么"的候选）
locale 约束: 该页有/没有 "Clear"/"confirm" 文案（有 → 可能弹确认；没有 → 大概率不弹）
数据约束: accounts.json 的组结构（组内 accounts 数组）
候选语义（备择解释，按可能性排）:
  ① 清空当前选中项（最常见于 grid）
  ② 清空当前组的全部账号（破坏性，通常要确认框 —— 与本页 locale 是否冲突？）
  ③ 清空筛选条件
判定所需的最小观测: 路 C 里点一次 Clear，看 accounts.json 是否变化
authority: unknown（缺运行期观测）
```

这样每条都**有结构证据、有候选集、有判定方法**，只是缺最后一步观测 —— 这才是可交付的 Unknown。

---

## 4. 别忘了一件已有的事：原版数据目录里有历史证据

`%APPDATA%\Cybersole` 是**YG 真实使用过的**（`settings.json` 里 `bearer`/`license` 有值，mtime 16:08）。
它里面的 `accounts.json` / `tasks.json` / `solvers.json` 结构，**本身就是行为的结果样本**：

- 组 → 账号的嵌套形状，能约束 `Add`/`Delete`/`Clear` 的候选集（②能否成立）；
- 若某个组里存在"空组"，说明 `Clear` 或 `Delete` 曾把它清空 → 支持 ②；
- 若所有组都非空，则 ① 更可能。

**只读、零风险、现在就能做**。做完再去走路 C，可以把候选集压到 1–2 个。

---

## 5. 一句话

> xref 这条链断了，我复核加扩大后同意；但**"要行为证据就得给我凭据"是错的** ——
> 让 YG 亲手点两下、我只读比哈希，就能把 31 条从 Unknown 变成 Observation。
> **在拿到之前，31 条写成"带候选集和判定方法的 Unknown"，而不是空白。**
