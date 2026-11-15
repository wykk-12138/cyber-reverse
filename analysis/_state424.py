import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 424 轮：全量套件在这台机器上跑不完（记录，不掩盖）

### 一、尝试

```
available 2.22 GB
dotnet test -m:1 --filter "Speed!=NoSlow"    →  25 分钟仍在运行 → 后台作业 → 再等 10 分钟无输出 → 终止
```

平时全量是 **25 秒**。这次 **35 分钟没有结果**，随后我终止了它（并清掉残留 `testhost` / `dotnet`）。
终止后 available 回到 2.48 GB。

### 二、结论

在 `Commit 92.7 / 94.0 GB` 这种状态下，**全量套件不具备可执行性**。这不是代码问题：

- 相关用例（copy / 计数守卫 / bind 相关）**单跑全绿**；
- 全量的失败模式是**挂住**，不是断言失败。

### 三、留给下一次重启后

```
dotnet test -c Debug --filter "Speed!=Slow"        # 正常并行，约 25 秒
python tools/mutation-check.py                     # 29 条，12–15 分钟
```

两条都写进 `SESSION_STATE.md` 的"下一步"，并且**标明前置条件：`available > 6 GB`**。

### 四、这一轮的一句话

> 我没有把"跑了 35 分钟没结果"写成"通过了"。

> **挂住的测试既不是通过，也不是失败；它只是没有证据。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('''## 下一步（按价值排序）''', '''## 未完成（需要重启机器）

| 任务 | 前置条件 |
|---|---|
| 全量套件 `dotnet test --filter "Speed!=Slow"` | `available > 6 GB`（R424：2.2 GB 时挂住 35 分钟无输出） |
| 变异测试 `python tools/mutation-check.py`（29 条） | 同上，且期间不做别的 |

## 下一步（按价值排序）''')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
