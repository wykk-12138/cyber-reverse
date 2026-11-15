import io
p = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 八、两种布局、两类证据（R269–R277 的产出，别忘）

### 1. 同一个东西可能有两种存法，判据要分别写

| 布局 | 形态 | 工具 |
|---|---|---|
| **A 合并式** | 一行里塞一批 `d__N` + lambda 表 | `tools/flow_dump.py` |
| **B 分行式** | 每个 `d__N` 各占一行，地址相邻 | `tools/row_groups.py` |

**教训**：R271 我按 A 去查 John Lewis，结论"走不通"；R272 发现它用 B ——
**判"这条路不通"之前，先确认自己试的是不是全部形态。**

### 2. 一张表里可能混着两类证据

| 类 | 来源 | 能否逐条对账 |
|---|---|---|
| `literal` | 直接读自一段字面量 | 能（`structure-token-*` 15/15、12/12） |
| `endpoint` | 按端点族叙述出来的行为模型 | 不能（`StartEcomSession` vs `Start`） |

落地：`StoreFlowSteps.Flow.Source`（默认 `Endpoint`）+ `StoreFlowSourceTests`。
**默认选更弱的一类，漏标只会低估。**

### 3. 子集家族会让"同时命中"看起来像矛盾

`0x03388fd2` 同时命中 `structure-token-multi`（8/15）与 `-single`（7/12）——
它不是骑墙，是**同族子集**。**遇到"两边都像"时，先考虑"它本来就是同一族的第三个"。**

### 4. 数字粘连是常态，不是例外

`356:SubmitPayment`、`140:SubmitShipping`、`150:GetStructureToken` —— 池子里相邻数字会粘。
**凡序号 > 200 一律复核；凡"步数"都不等于"序号差"。**

### 5. 一条线吃完要写"吃完"

流程序号这条线（R269–R277）最后落在：18 条流水线 / 141 步、2 条被证实为字面量、
14 条属未建模商店。**写清"到此为止 + 除非有新证据源"，比继续硬挖更有价值。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('METHOD.md: four new lessons recorded')
