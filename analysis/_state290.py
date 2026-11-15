import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 290 轮：把八条流钉成**摘要指纹**（digest），并机械校验序号

### 一、先机械核对序号（不靠眼看）

对每条流，取它字面量的 `(名, 序号)`，再和复刻件的逐条比 —— 允许"粘连位"（`498`→`49` 这类）：

```
structure-token-multi  15/15    structure-token-single 12/12
popmart                24/24    demandware-classic     12/12
demandware-dual        15/15    collectplus-app        17/17
nike                   16/16    johnlewis              17/19（另 2 步来自 lambda 行：FindProduct/AddToCart）
```

**八条流的名字、顺序、序号全部可解释。**

### 二、加一条 `StoreFlowDigestTests`

把每条流的 `名:序号` 按顺序连成一个字符串，作为**指纹**写进测试：

```csharp
["structure-token-single"] = "EditLine:40|AddToCart:41|…|ProcessPayment:51",
```

于是**任何一次改动都会改指纹** —— 想改就必须同时改这张表，也就必须带上证据。

> 这条测试正是针对 R287 那类事故：当时 `structure-token-single` 的错步**悄无声息地**变成了"新真相"。

### 三、验证

```
StoreFlowDigestTests              2 通过 / 0 失败
完整套件                          1443 通过 / 0 失败 / 2 跳过（21 s）
Commit 16.55 GB / 可用 18.51 GB
```

### 四、这一轮的一句话

> 到此为止，八条流的每一句话都能追到池子里的一个地址 —— 而且**改不动**，除非你说清依据。

> **可对账还不够；要让它"改不动"，才算钉住。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 290 轮（八条流加 `StoreFlowDigestTests` 指纹；序号机械核对全部通过）。

---

## 八条流：已钉住

| 校验 | 结果 |
|---|---|
| 名字 / 顺序 / 序号 vs 字面量 | 15/15、12/12、24/24、12/12、15/15、17/17、16/16、17(+2 lambda)/19 |
| 指纹测试 `StoreFlowDigestTests` | **2 通过**；每条流的 `名:序号` 串都写进表里 |
| 效果 | 任何改动都会改指纹 → 必须同时更新表 → 必须带证据 |

地址记在 `StoreFlowSteps` 每条流的注释里（`nike` 两条、`johnlewis` d__ 行 + lambda 行）。

## 验证状态

```
全量 mutation-check   24 / 24 fired（R286）
完整套件              1443 通过 / 0 失败 / 2 跳过（R290）
Commit 16.55 GB / 可用 18.51 GB
```

## 下一步

1. B 类 31 个缺口（结构差异）—— 若要做，先抽行控件；
2. 14 条未定名流水线需外部知识；
3. `docs/RESUME.md` 的数字需要同步（1443 / 8 条流）。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
