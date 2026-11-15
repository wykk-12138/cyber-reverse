import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## R294：再找一轮证据 + 在源码里标「推断」

### 1. 换匹配方式又找到 3 条

上一轮只做"整条路径在池子里"，这一轮加了两条更宽的判据（**URL 里包含该路径**、**去掉模板占位符按前缀查**）：

```
/api/v1/carts/{c.Session.CartId}         <- https://hbx.com/api/v1/carts
/api/v1/carts/{c.Session.CartId}/items   <- https://hbx.com/api/v1/carts
/v1/carts/{c.Session.CartId}/items       <- api/v1/carts
```

→ 无证据从 **22 → 18**（HBX 的三条其实是同一族，账本按路径去重后减 3）。

### 2. 剩下 18 条：在源码里逐条标 `inferred: no image evidence (R294)`

标记落在**使用该路径的代码行**上（不是文档注释），共 19 处标记覆盖 18 条路径（HBX 三条共用两行）。

于是读那段流程代码的人，**不会把推断当成证据**。

### 3. 棘轮升级

`EndpointEvidenceRatchetTests` 新增第三条：**每个用无证据路径的文件里必须出现这句标记**。
少了任何一处，测试就红。

## R294 的诚实结论

| 判定 | 条数 |
|---|---|
| 逐字命中 | 44 |
| 片段组成（弱证据） | 23 |
| **URL 包含 / 前缀命中** | **3** |
| **仍无证据（已标推断）** | **18** |

**这 18 条没有被删除，也没有被当成证据** —— 它们现在是"已知的推断"，而不是"看起来像证据的东西"。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ENDPOINT_LEDGER updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 294 轮：再找一轮证据（22 → 18），并把剩下的**逐条标成"推断"**

### 一、换判据又捞回 3 条

上一轮只认"整条路径原样在池子里"。这一轮加上 **URL 包含** 与 **去模板后按前缀查**：

```
/api/v1/carts/{c.Session.CartId}         <- https://hbx.com/api/v1/carts
/api/v1/carts/{c.Session.CartId}/items   <- https://hbx.com/api/v1/carts
/v1/carts/{c.Session.CartId}/items       <- api/v1/carts
```

无证据 **22 → 18**。

### 二、剩下 18 条：在**代码行**上标 `inferred: no image evidence (R294)`

19 处标记，覆盖 18 条路径（HBX 三条共用两行）。中途发现 6 处先落在了 `///` 注释行上 ——
已重排到真正的代码行（`PopMartEndpoints.cs:8` 除外，那条路径只出现在文档注释里）。

### 三、棘轮加第三条

`EndpointEvidenceRatchetTests`：**每个用无证据路径的文件必须含这句标记**，少一处就红。

### 四、验证

```
EndpointEvidenceRatchetTests   3 通过 / 0 失败
完整套件                       1449 通过 / 0 失败 / 2 跳过（21 s）
Commit 18.96 GB / 可用 17.09 GB
```

### 五、这一轮的一句话

> 上一轮我把 22 条"编的"翻出来；这一轮先把能救的救回来 3 条，**再给救不回的贴上标签**。

> **账本让问题可见，标记让问题在"读代码的地方"也可见 —— 两者缺一，下一个人还是会在同一个坑里踩一脚。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 294 轮（端点：22 → **18 条无证据**（换判据捞回 3 条），剩下 18 条**已在代码行标"推断"**）。

---

## 端点证据账（R294）

| 桶 | 条数 |
|---|---|
| 逐字命中 | 44 |
| 片段组成（弱证据） | 23 |
| URL 包含 / 前缀命中 | 3 |
| **无证据（已标 `inferred:`）** | **18** |

- 标记落在**代码行**上：`inferred: no image evidence (R294)`（19 处覆盖 18 条）
- 棘轮 3 条：条数不增长 / 每条仍在原文件 / **每个文件必须有该标记**
- 文档：`docs/ENDPOINT_LEDGER.md`

## 验证状态

```
完整套件   1449 通过 / 0 失败 / 2 跳过（R294）
mutation   24/24 fired（R286）
Commit     18.96 GB / 可用 17.09 GB
```

## 下一步

1. 这 18 条里，`/api/beast`、`/v1/buys`、`/view/resources/getUserInfo` 是典型的"照风格编"，
   可以考虑改成更保守的形态（或在无证据时走通用路径）；
2. 其余按 B 类结构差异处理。

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
