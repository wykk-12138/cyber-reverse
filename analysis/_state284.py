import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 284 轮（**静态审计发现 2 条哑掉的 mutation**，已修好并验证：anchors 24/24）。

---

## mutation 护栏：24 条**全部是活的**

审计方法（不跑测试，纯字符串）：每条 mutation 的 `find` 锚点到文件里找一遍。

```
修前：anchors present 22 / 24
  DEAD: round 127 -- Flush 先出队再判 sink（注释被 R155 改写）
  DEAD: round 164 -- PARITY.md UI 计数（锚点写 77/24，文档已是 83/26）
修后：anchors present 24 / 24
验证：--only "round 164" → 2 条 guard fired → restored tree GREEN
```

**新工具**：`python tools/mutation-audit.py`（零成本，动完源码就可以先跑一遍）。

**规律**：**护栏自己也会腐烂** —— 文件改了、文档数字改了，锚点就静默失效，而它还在报告里算数。

## 状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation anchors 24/24 活；全量 24 条待重启后跑（12–15 分钟）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 41.4 GB / 可用 6.1 GB   ← 低于 8 GB 硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
