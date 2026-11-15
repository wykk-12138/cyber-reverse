import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 299 轮（端点 18 条拆成 **10 真发 + 7 仅文档**；我上一轮冤枉了 `/api/beast`）。

---

## 端点账修正后的准确形态

| 类 | 条数 | 严重度 | 处理 |
|---|---|---|---|
| 真的会发出去、无池子证据 | **10** | 高 | 代码里标 `inferred`，棘轮 `Sent ≤ 10` |
| 只出现在文档注释 | **7** | 中 | 是"断言"不是"行为"；**待运行时复核** |
| 逐字命中 / 片段 / URL 包含 | 67 | — | 直接用 |

**已纠正的误判**：`/api/beast` 只存在于 `BstnFlow.cs` 的文档注释（"until a live capture showed otherwise"），
**代码并不发它**。上一轮我把它当成伪造请求。

**7 条文档断言的证据来源是现场抓包/页面观察**（路径运行时拼接，本来不会进池子）→
"池里查不到"既不能否定也不能证实，记为待运行时复核。

## 验证状态

```
完整套件   1456 通过 / 0 失败 / 2 跳过（R299）
mutation   24/24 fired（R286）
Commit     23.59 GB / 可用 14.61 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
