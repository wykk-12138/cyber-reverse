import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 266 轮（补上欠了十轮的**完整**套件：1436 通过 / 0 失败 / 2 跳过，无残留）。

---

## 验证状态（这次是**全套**，不是子集）

```
完整套件 Speed!=Slow   1436 通过 / 0 失败 / 2 跳过（22 s）
残留                   chrome 0 / 临时 profile 0
Commit 38.95 GB / 可用 7.35 GB
```

上一次全套是 R256（1434）；R257–R265 十轮只跑过子集。**这十轮的改动全部通过。**

## 新纪律：报"绿"必须说口径

> **子集绿 ≠ 全套绿。** 报告里写"绿"时必须说清是哪一个；不写口径的"绿"和"估的数字"是同一类东西。

## 下一轮主线（缺口已收敛到结构问题）

`docs/BINDING_BACKLOG.md`：A 类只剩 2 个（都缺数据源），B 类 31 个建议保持"结构差异"。
所以主线换方向：

1. **抽行控件**（`FilterRow` / `ActionRow` / `ProfileCsvRow`）——一次一个，真正的结构工作；
2. 或回到**功能深度**：六条流程序号缺口、`X-Shopify-Generated-Cart-Token` 方向 ——
   这些比成员名更贴近"功能 1:1"。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
