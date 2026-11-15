import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 307 轮：把 cookie / 参数两条守卫也纳入变异检查 —— 又是**两次装饰性**

### 一、加了两条变异

| 变异 | 目标守卫 |
|---|---|
| round 297 去掉 `ffid` 的 `(R297)` 标记 | `CookieEvidenceRatchetTests` |
| round 298 去掉 `productTemplateId` 的 `(R298)` 标记 | `QueryParamEvidenceRatchetTests` |

### 二、首轮结果：两条都是 `DECORATIVE`

原因和 R305 一模一样：**这两个文件里同一个标记串出现多次**（文档行 + 多个代码行），
`replace(…, 1)` 只改掉**第一处**，而第一处恰好在文档行（测试已忽略文档行）→ 仍然绿。

### 三、修法：`"all": True`

mutation-check 早就支持 `all` 字段（`replace(..., -1)`），只是我之前没用。加上后：

```
round 297 -- an unbacked cookie loses its inferred marker      [guard fired]
round 298 -- an unbacked query param loses its inferred marker [guard fired]
restored tree: GREEN
```

### 四、验证

```
三条证据棘轮的变异   297 / 298 / 294 全部 fired
完整套件             1458 通过 / 0 失败 / 2 跳过（24 s）
mutation 总数        29（29/29 锚点存在）
```

### 五、这一轮的一句话

> 同一个坑我这轮又掉了一次：**"改一处"和"改全部"在守卫测试里是两件完全不同的事。**

> **写变异的人必须先想清楚：我改的是不是它真正检查的那一处。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 307 轮（cookie / 参数守卫纳入变异检查；两次装饰性 → 用 `"all": True` 修好，两条都 fired）。

---

## 变异检查：29 条，三条证据棘轮全部有变异背书

| 变异 | 守卫 | 状态 |
|---|---|---|
| round 290 流序号 45→44 | `StoreFlowDigestTests` | fired |
| round 292 错误目录标题 | `ErrorCatalogDigestTests` | fired |
| round 294 端点标记移除 | `EndpointEvidenceRatchetTests` | fired |
| **round 297 cookie 标记移除** | `CookieEvidenceRatchetTests` | **fired（`all: true`）** |
| **round 298 参数标记移除** | `QueryParamEvidenceRatchetTests` | **fired（`all: true`）** |

**踩坑**：同一个标记串在文件里出现多次 → `replace(…, 1)` 只改第一处（多半是文档行）→ 守卫仍绿。
**mutation 里要改"全部"，不是"一处"。**

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条，锚点 29/29；新两条已单跑 fired
Commit     36.6 GB / 可用 8.8 GB   ← 已贴硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
