import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''理由：Commit 是账本不是占用；本轮在 Commit 30.85→32.26 GB、可用 11.3→9.84 GB 的情况下完成了小步工作。''',
'''理由：Commit 是账本不是占用；本轮在 Commit 30.85→32.26 GB、可用 11.3→9.84 GB 的情况下完成了小步工作。

**实测可回收的一步**：`dotnet build-server shutdown` 之后 Commit **32.26 → 31.09 GB**、可用 9.84 → 11.0 GB
（约 1.2 GB）。**每个编译轮结束时都要跑它**，比 purge 便宜且不需要管理员。''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('recorded the build-server recovery')
