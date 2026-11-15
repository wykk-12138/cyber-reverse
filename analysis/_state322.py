import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 322 轮：补上 R321 的验证 —— 全套 **1474 通过 / 0 失败**

### 一、为什么这轮只做验证

R321 改了 `GoatFlow.GetHomeAsync`（新增 CSRF 兜底），但当时内存 4.56 GB，没跑测试。
**一个改了源码又没跑测试的轮次，等于欠了一笔债。** 这一轮还掉。

### 二、结果

```
完整套件   1474 通过 / 0 失败 / 2 跳过（21 s）
```

条数与 R319 相同 —— 说明兜底改动**没有破坏任何既有行为**（Goat 相关测试全绿）。

### 三、内存

```
跑前 5.05 GB → 跑后 4.45 GB → build-server shutdown 之后回一点
```

在全套（含编译）的前提下，这个水位还能跑完 21 秒。

### 四、这一轮的一句话

> 上一轮我"改完就走"，这一轮回来补验证 —— 两轮加起来才算一次完整的改动。

> **改动 + 验证才算一步；只做一半，账本就是虚的。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 322 轮（R321 的债还了：全套 **1474 通过 / 0 失败 / 2 跳过**）。

---

## 验证状态（R322 时点，全套）

```
完整套件   1474 通过 / 0 失败 / 2 跳过（21 s）
缺口       17（real = ceiling = 账本标题）
UI 类      104 声明 / 31 不可达
mutation   29 条 / 锚点 29/29（全量上次 R307）
```

R321 的 Goat CSRF 兜底**没有破坏既有行为**（Goat 相关测试全绿）。

## 状态

```
Commit 44.4 GB / 可用 4.45 GB   ← 明显低于硬线
```

## 下一步（重启后）

1. 全量 `mutation-check`（29 条，约 15 分钟）；
2. 功能深度：`docs/ENDPOINT_LEDGER.md` 里 10 条真实发送但无出处的端点，
   按 R321 的方法逐个查"该商店在池子里有一条有出处却没用上的路径"。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
