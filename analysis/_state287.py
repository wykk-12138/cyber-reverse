import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 287 轮：从字面量改正 `structure-token-single` —— 一条流里**两个步骤是错的**

### 一、起因

R274 对账时 `structure-token-single` 只命中 11/12。当时记成"缺 `GetMerchantCode`"，
这一轮读了字面量原文（`0x034b23a5`）才发现：**不是缺，是错。**

### 二、字面量原文（含它自己的 lambda 表）

```
<EditLine>d__40 <AddToCart>d__41 <GetCheckout>d__42 <GetShippingRate>d__43
<SubmitShipping>d__44 <CalculateTaxes>d__45 <GetStructureToken>d__46
<CreateTransaction>d__47 <SubmitPayment>d__48 <GetPayPalToken>d__49
<SubmitPayPal>d__50 <ProcessPayment>d__51
  … b__43_1 GetShippingRate / b__44_1 SubmitShipping / b__45_1 CalculateTaxes /
     b__46_1 GetStructureToken / b__49_1 GetPayPalToken / b__50_1 SubmitPayPal / b__51_1 ProcessPayment
```

**lambda 表逐条对上** —— 所以这 12 步是硬证据。

### 三、复刻件错在哪

| 项 | 原来 | 正确 |
|---|---|---|
| 第 4 步 | `GetMerchantCode(37)` | **不存在**（`GetMerchantCode` 是 multi 的第 38 步） |
| 税那一步 | **缺失** | `CalculateTaxes(45)` |
| 序号 | 34–45 | **40–51** |

改动后：12 步、序号 40–51、与字面量**逐条一致**。

### 四、更值得记的是：**守卫里也写着同一个错**

改完代码后 `TheStructureTokenFlowsShareTenSteps` 红了两次：

```
Assert.DoesNotContain("CalculateTaxes", single)   // 「税只在 multi 里」
Assert.Contains("GetMerchantCode", shared)        // 「共享集里有 GetMerchantCode」
```

**这两条断言把缺陷写成了不变量。** 已按字面量改正，并补上真正区分两条流的三对：

```
multi 独有: FindProductMulti, GetMerchantCode      single 独有: EditLine
两者都有:   CalculateTaxes（共享 10 个之一）
```

### 五、验证

```
Stores 编译                        0 错误
流相关测试                          30 通过 / 0 失败
完整套件                            1442 通过 / 0 失败 / 2 跳过（21 s）
Commit 13.62 GB / 可用 20.39 GB
```

### 六、这一轮的一句话

> 一条被判为"字面量派生"的流，里面仍有两步是错的 —— 而且**错在同一个方向**：
> 把 multi 的步骤挪到 single、把 single 的步骤漏掉。

> **"来源标对了"不等于"内容对了"。** 守卫写下的不变量，可能是缺陷的复印件。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 287 轮（按字面量改正 `structure-token-single`：去掉 `GetMerchantCode`、补 `CalculateTaxes`、序号改 40–51）。

---

## 验证状态

```
全量 mutation-check   24 / 24 guard fired（R286）      restored tree: GREEN
完整套件              1442 通过 / 0 失败 / 2 跳过（R287，21 s）
残留                  chrome 0
Commit 13.62 GB / 可用 20.39 GB
```

## 本轮改正（有硬证据）

字面量 `0x034b23a5` 的 12 步 + 它自己的 lambda 表（`b__45_1 CalculateTaxes` 等）证明：

| 项 | 原来 | 现在 |
|---|---|---|
| `structure-token-single` 第 4 步 | `GetMerchantCode(37)` | 不存在（那是 multi 的 38 步） |
| 税那一步 | 缺失 | `CalculateTaxes(45)` |
| 序号 | 34–45 | **40–51** |

**并且守卫里那两个断言也曾把缺陷写成不变量**（`DoesNotContain("CalculateTaxes", single)`、
`Contains("GetMerchantCode", shared)`）—— 已一并改正。

**教训：来源标对了 ≠ 内容对了；守卫可能写着缺陷的复印件。**

## 下一步

1. 其余 4 条 `FlowSource.Endpoint` 的流：逐条找字面量、能标的改成 `Literal` 并核对内容；
2. B 类 31 个缺口仍是结构差异（`docs/BINDING_BACKLOG.md`）。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
