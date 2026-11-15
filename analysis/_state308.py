import io
p = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 九、守卫与证据（R296–R307 的六条硬教训）

### 1. **判方向 > 判存在**

同一个字符串，可能是"发出去的头"，也可能是"记在响应对象上的诊断"。
`X-Cyb-Transport` 看着像自己编的指纹头，实际写在响应的 `Headers[...]` 上，**根本不发**。
**先问"它往哪儿去"，再问"它在不在"。**

### 2. **"没有出处"有三种**

| 种 | 例子 | 处理 |
|---|---|---|
| 真发了、无出处 | `/v1/buys`、`/account/verify` | 代码行标 `inferred:` + 棘轮 |
| 只是写着、没发 | `/api/beast`（只在文档注释里） | 记为"待运行时复核" |
| 我没看懂它在哪 | `X-CSRF-TOKEN` 其实池里有小写 `x-xsrf-token` | 先复核自己的查法 |

### 3. **文案/名字差异 ≠ 功能差异**

`Settings.*` 有 238 个文案键，复刻件只引用了约六成 —— 但抽样三条（`BackupNow`、`ThreeDS`、`WindowMode`）
**全都有实现，只是标签是字面量**。这类计数**不能当缺陷探测器**，更不该进棘轮。
`Settings.Nav.*` 16 条里，**1 条是分组标题不是页面**（`ADVANCED`）—— 数量 ≠ 可导航项数。

### 4. **守卫自己会腐烂；新守卫必须立刻做变异检验**

- 锚点漂了 → 工具静默 skip，还在报告里算数（R284 修好 2 条哑护栏）；
- 断言比变异松 → "装饰性守卫"（R305 抓出我自己刚写的一条）。

### 5. **断言要落在"行"上，不是"文件"上**

`Assert.Contains(marker, 整个文件)` 会被同文件里**别的**标记行满足。
改成"**每个使用该名字的代码行都必须带标记**"后，一口气抓出 10 处漏标（R306）。

### 6. **变异要改"全部"，不是"一处"**

`replace(find, replace, 1)` 只改第一处，而第一处常在文档行（断言已忽略）→ 变异无效。
mutation-check 支持 `"all": true`；R307 用它才让两条新变异正常 fired。

### 7. 附：**先读守卫，再动手**

R300 我把 `ADVANCED` 加成第 16 个设置页，被几十轮前写的
`SettingsShellTests.AdvancedIsAGroupCaptionNotAPage` 拦下（连带红 4 条）。
**守卫记着的知识，往往正是我此刻缺的那一条。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('METHOD.md: section 9 added')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 308 轮（把 R296–R307 的六条教训并进 `docs/METHOD.md` 第九节；未编译）。

---

## `docs/METHOD.md` 第九节：守卫与证据

1. **判方向 > 判存在**（`X-Cyb-*` 是响应侧诊断，不发出去）；
2. **"没有出处"有三种**（真发了 / 只是写着 / 我没看懂它在哪）；
3. **文案/名字差异 ≠ 功能差异**（`Settings.*` 六成引用率是假缺口；`ADVANCED` 是标题不是页）；
4. **守卫会腐烂，新守卫必须立刻做变异检验**（哑护栏 / 装饰性守卫）；
5. **断言落在"行"上，不是"文件"上**（R306 因此抓出 10 处漏标）；
6. **变异要改"全部"，不是"一处"**（`"all": true`）；
7. 附：**先读守卫，再动手**。

## 状态（未改代码）

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
Commit     40.5 GB / 可用 6.9 GB   ← **低于硬线，建议重启**
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
