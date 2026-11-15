import io
p = r'D:\projects\cyber-reverse\replica\docs\FLOW_SEQUENCES.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## 十二、拿复刻件的 `StoreFlowSteps` 对账：**它其实有两类行**（R274）

用 18 条恢复出来的段去对 `src/Cybersole.Stores/Flows/StoreFlowSteps.cs` 里的 8 条流：

| 流 | 步数 | 命中 | 最佳段 |
|---|---|---|---|
| **structure-token-multi** | 15 | **15 / 15** | `0x034b14b8` |
| **structure-token-single** | 12 | **11 / 12** | `0x034b23a5`（缺 `GetMerchantCode`） |
| johnlewis | 19 | 4 / 19 | `0x3371cea` |
| nike | 16 | 2 / 16 | `0x3371cea` |
| demandware-classic | 12 | 3 / 12 | `0x034b23a5` |
| demandware-dual | 15 | 2 / 15 | `0x03390d79` |
| popmart | 24 | 0 / 24 | — |
| collectplus-app | 17 | 3 / 17 | `0x3378cb1` |

### 两类行，证据强度完全不同

| 类 | 例子 | 命中率 | 说明 |
|---|---|---|---|
| **字面量派生** | `structure-token-multi` / `-single` | **15/15、11/12** | 直接读自一段字面量 → **被这次恢复完全证实** |
| **端点派生** | nike / popmart / johnlewis / demandware / collectplus | 0–4 | 当年是**按端点族"讲出来"的**，名字与字面量里的方法名不是同一套 |

例如复刻件写 `StartEcomSession`，字面量里是 `Start`；写 `SubmitConsignment`，字面量里是 `SubmitShipping`。
**这不是错，是两种不同的东西**：一类是"镜像里的步骤表"，一类是"我们据端点推断的行为模型"。

### 结论（写进对账纪律）

> **`StoreFlowSteps` 里的行必须标清来源**：`literal`（可直接对账）还是 `endpoint`（叙述性，不可与字面量逐条比对）。
> 不标来源的"1:1"，是把两种证据混在一起算。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('FLOW_SEQUENCES.md: the two-class finding is recorded')
