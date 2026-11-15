import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 297 轮（cookie 名审计：5 个 → 2 有证据 / **3 标推断**（`NIKE_COMMERCE_COUNTRY`、`ffid`、`sbsd`））。

---

## 会"发出去的东西"的账本（三张，都在 `docs/ENDPOINT_LEDGER.md`）

| 类别 | 结果 |
|---|---|
| 端点 | 89 = 44 逐字 + 23 片段 + 3 URL 包含 + **18 无证据（标 `inferred`）** |
| 请求头 | 16 = 13 逐字 + 2 内部诊断（不发）+ **1 改名已修**（`x-xsrf-token`） |
| cookie | 5 = 2 有证据 + **3 无证据（标 `inferred`）** |

棘轮：`EndpointEvidenceRatchetTests`（3）、`CookieEvidenceRatchetTests`（2）。

## 验证状态

```
完整套件   1454 通过 / 0 失败 / 2 跳过（R297）
mutation   24/24 fired（R286）
Commit     21.31 GB / 可用 15.99 GB
```

## 下一步

- 同一方法还能查**查询参数名**（`?foo=`）与 **GraphQL 操作名**（已查：9 条候选全真）；
- 或者回到 B 类 31 个结构差异。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
