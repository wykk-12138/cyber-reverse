import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 内存纪律（R236 修订）')
head = '''最后更新：第 237 轮（补上三轮欠账：全套 1428 通过 / 0 失败 / 2 跳过；修掉一个只在批量失败的探针测试）。

---

## 欠账状态：**已清空**

```
完整套件 Speed!=Slow   1428 通过 / 0 失败 / 2 跳过（20 s）
跑完残留               chrome 0 / 临时 profile 0
Commit 32.59 GB / 可用 10.26 GB（峰值 35.24）
```

**本轮修掉的测试问题**：`GlobalPruneTests.ChromeIsGone` 单独过、批量挂 —— 探针在隐身补丁生效前读了文档。
改成**有上限重试**（20 × 100 ms），**断言一字未改**。这是"给它时间"，不是"放宽标准"。

'''
out = lf[:i] + head + lf[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
