import io
p = r'D:\projects\cyber-reverse\replica\docs\_r205.md'
t = io.open(p, encoding='utf-8').read()
old = """### 五、验证

```
快测 Speed!=Slow      1378 通过 / 0 失败 / 2 跳过   （连跑三次）
新增测试              HomePageParityTests（4 条）
视图/GUI              目标已可启动并快照（pid 189264）
```
"""
new = """### 五、验证

```
快测 Speed!=Slow      1378 通过 / 0 失败 / 2 跳过   （连跑三次；崩溃后重跑仍是这个数）
新增测试              HomePageParityTests（4 条）
视图/GUI              目标已可启动并快照（pid 189264）
mutation-check        ✗ 未完成 —— 跑到一半机器内存爆了，DSH 与 IDA 一起崩
```

**这一项要如实记：`mutation-check` 没有跑完。** 崩溃后我做了三件事确认树没坏：

1. 没有残留进程（`Cybersole` / `python` / `dotnet` / `testhost` 全无）。
2. 比对 `tools/.mutation-backup` 里 14 个备份与线上文件：**逐行 diff 全为 0**（只有换行符差异 —— 备份写成 LF，线上是 CRLF），
   也就是**没有留下未还原的变异**。
3. 单跑一次全量：1378 绿。

`mutation-check` 留到下一轮**单独**跑，不再和别的任务并行。
"""
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('patched')
