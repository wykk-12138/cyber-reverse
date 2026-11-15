import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 已测出的几何数据')
head = '''最后更新：第 220 轮（重启后清账：完整套件 1406 绿 + mutation 23 条全开；确认"漏水点"关掉后同样重活只堆到 17.8 GB；启动画面寿命 ≥4.35 s）。

---


## 欠账状态：**已清空**（R220）

```
完整套件 Speed!=Slow   1406 通过 / 0 失败 / 2 跳过
mutation-check         23 条守卫全部 fired，restored GREEN
测试临时 profile 残留   0（R219 修复在全套规模下成立）
```

## 内存纪律（R219-R220 的结论，别再忘）

| 数字 | 会不会影响干活 | 处理 |
|---|---|---|
| Commit 高 | **不影响**，是账本 | purge 无用；不归零也能继续用 |
| 可用物理掉到 4-5 GB | **影响** | `analysis/memreset.ps1`（需管理员）实测 +1~2.5 GB |
| Repurposed 3-4 GB | 不影响（可回收） | 重启才显示归零 |

**根因已修**：`ChromiumBridge.DisposeAsync` 现在删掉自己创建的 `cyb-chromium-*`（此前从不删，一天积 9072 个 / 46.7 GB）。

'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
