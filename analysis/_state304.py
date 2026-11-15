import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 304 轮：把那个"两次出现的 flake"从**测代理**改成**测本体**

### 一、flake 是什么

`GlobalSurfaceTests.NoNameIsAdvertisedWithoutAProperty` 断言：`window` 的自有属性名集合，必须与记录表完全一致。

它两次在全套里红、单独跑绿（R236 一次、R303 一次）。R206 已经为它写了等待器，注释里写着：

> "measured one suite run in eight ending with `extra[chrome]`，即 prune 已跑、页面报告 complete，
> 而对象在测计数的那一刻回来了。"

### 二、这次找到的根因：**它等的是长度，测的是集合**

```csharp
// SettleAsync：等 Object.getOwnPropertyNames(window).length 稳定
```

**长度稳定 ≠ 集合稳定。** 只要 Chromium 在同一长度上换掉一个名字（加一个、减一个），
等待器就会认为"稳了"，而断言比的是集合 —— 于是红。

### 三、修法（measurement fix，不动任何断言）

新增 `BrowserProbe.SettleNamesAsync`：采样 `Object.getOwnPropertyNames(window).sort().join(',')`，
**要求三次完全相同**（60 ms 间隔，上限 60 次 ≈ 3.6 s）。`ProbeAsync` 在原有 `ReadyAsync` 之后调用它。

> 这是"测本体而不是测代理"的修法 —— 与 R237 修 `ChromeIsGone` 同一类（加上限重试、断言不动）。

### 四、验证（连跑两次全套）

```
run1   1458 通过 / 0 失败 / 2 跳过（22 s）
run2   1458 通过 / 0 失败 / 2 跳过（22 s）
```

两次都绿。**注意**：flake 的定义就是"不常出现"，两次绿不能证明修好了；
但它现在测的东西**和断言完全一致**，从原理上不该再有这个偏差。

### 五、这一轮的一句话

> 前两次我都按纪律"只记录不改"；这次改，是因为找到了**机制上的解释**，而不只是"它又红了"。

> **改 flake 的门槛不是"它烦人"，是"我能说出它为什么会红"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 304 轮（flake 根治：`SettleAsync` 等长度、断言比集合 → 新增 `SettleNamesAsync` 等集合；连跑两次全绿）。

---

## 那个 flake：已从机制上修掉

| 项 | 内容 |
|---|---|
| 症状 | `NoNameIsAdvertisedWithoutAProperty` 全套里偶发红（R236、R303 各一次），单独跑绿 |
| 根因 | 等待器 `SettleAsync` 等的是 **名字个数**，断言比的是 **名字集合**；同长度换名不会被发现 |
| 修法 | 新增 `BrowserProbe.SettleNamesAsync`：`getOwnPropertyNames(window).sort().join(',')` **三次相同**（上限 ≈3.6 s） |
| 断言 | **一行没改** |
| 验证 | 全套连跑两次：1458 通过 / 0 失败 / 2 跳过 |

**纪律补充**：改 flake 的门槛不是"它烦人"，是"我能说出它为什么会红"。

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R304，连跑两次）
mutation   24/24 fired（R286）
Commit     30.35 GB / 可用 12.37 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
