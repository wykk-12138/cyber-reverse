import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 292 轮：错误目录 **13/13 标题与 13/13 详情逐字命中**，已钉成测试

### 一、审的是什么

`ErrorCatalog` 是原版 Settings → Need Help 那一页的内容 —— **属于产品表面**：
同一个故障，用户应该看到同一段解释。所以它必须逐字对。

### 二、结果：全部逐字命中

```
复刻件条目                 13（General 6 / Shopify 6 / Footsites 1）
标题在池子里逐字命中        13 / 13
详情句子在池子里逐字命中     13 / 13
池子里带 [Tag] 前缀的标题    13  ← 数量与复刻件相同，无遗漏
```

中途一次"未命中"是**我自己的正则错**：标题里有转义引号
`[Shopify] Tasks hanging on \\"Getting Shipping Rates\\"`，我的第一版正则截在 `\\"` 处。
修正后 13/13。

### 三、加三条测试 `ErrorCatalogDigestTests`

1. 恰好 13 条、标题去重后仍是 13、且与记录的 13 个标题逐字相同；
2. 标签分组必须是 **General 6 / Shopify 6 / Footsites 1**；
3. 每条必须有 `[Tag]` 前缀、非空 `Id` 与非空 `Detail`。

### 四、验证

```
ErrorCatalogDigestTests   3 通过 / 0 失败
完整套件                  1446 通过 / 0 失败 / 2 跳过（23 s）
Commit 17.14 GB / 可用 18.26 GB
```

### 五、这一轮的一句话

> 这条"逐字命中"是我这几十轮里最硬的一次对齐：**不是"结构相似"，是同一句话。**

> 而它一开始还假报了一个缺口 —— **审证据的人，自己的工具才是最该先被审的。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 292 轮（错误目录 **13/13 标题 + 13/13 详情逐字命中**；新增 `ErrorCatalogDigestTests`）。

---

## 错误目录：逐字对齐（最硬的一类对齐）

| 项 | 结果 |
|---|---|
| 条目 | 13（General 6 / Shopify 6 / Footsites 1） |
| 标题逐字命中池子 | **13 / 13** |
| 详情逐字命中池子 | **13 / 13** |
| 池里 `[Tag]` 前缀标题数 | 13（与复刻件同数，无遗漏） |
| 守卫 | `ErrorCatalogDigestTests`（3 条：13 条标题、6/6/1 分组、前缀与必填） |

**踩过的小坑**：第一次报"1 条未命中"，是我正则截在转义引号 `\\"` 处 —— 修正后 13/13。

## 验证状态

```
完整套件   1446 通过 / 0 失败 / 2 跳过（R292）
mutation   24/24 fired（R286）
Commit     17.14 GB / 可用 18.26 GB
```

## 下一步（可选方向，按证据强弱排）

1. **HTTP 头/接口清单**逐条对账（池里有大量 endpoint 片段，可与复刻件的端点表比）；
2. B 类 31 个缺口仍是结构差异，暂不动；
3. `docs/RESUME.md` 数字需随 1446 同步。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
