import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 298 轮（查询参数审计：42 个里 38 有证据、**4 标推断**；四类合并账 152 条 / 25 标推断）。

---

## 四类"会发出去的东西"的合并账（权威：`docs/ENDPOINT_LEDGER.md`）

| 类别 | 总数 | 有证据 | 已标推断 | 棘轮 |
|---|---|---|---|---|
| 端点 | 89 | 67 | **18** | `EndpointEvidenceRatchetTests`（3） |
| 请求头 | 16 | 13 | 1（改名已修 `x-xsrf-token`） | — |
| cookie | 5 | 2 | **3** | `CookieEvidenceRatchetTests`（2） |
| 查询参数 | 42 | 38 | **4** | `QueryParamEvidenceRatchetTests`（2） |
| **合计** | **152** | **120** | **25** | 7 条测试 |

**25 条推断全部在源码里带 `inferred: no image evidence (Rxxx)` 标记**，且有棘轮保证数量不增长、标记不被删。

## 验证状态

```
完整套件   1456 通过 / 0 失败 / 2 跳过（R298）
mutation   24/24 fired（R286）
Commit     22.59 GB / 可用 15.21 GB
```

## 下一步

- 25 条推断里，`/api/beast`、`productTemplateId`、`NIKE_COMMERCE_COUNTRY` 最像纯编造，可考虑改成更保守的形态；
- 或者回到 B 类 31 个结构差异。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
