import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 369 轮：一份"差异账本"（`docs/DEVIATIONS.md`），以及一次内存处置

### 一、为什么写这份文档

缺口数字（17 / 18）回答"还差什么"；**它不回答"哪些差异是故意的"**。
这一程里我接受了不少差异（273 处形状、tab 数、inferred URL、类型不可推断的留白），
这些散落在多份文档里，没人能一眼看全。所以单独成册：`docs/DEVIATIONS.md`，七节，

> 每条都写"为什么接受"，而不是只写"有差异"。

### 二、内存处置

`available` 掉到 **2.87 GB**（commit 51 GB）。处置：

1. 关掉原版 `Cybersole.exe`（787 MB，验证任务已完成，可随时重启）；
2. `dotnet build-server shutdown`；
3. **不做**变异测试（29 轮编译）—— 改为只跑文档守卫（57 个，1m14s）。

### 三、验证

```
文档守卫   57 通过 / 0 失败
内存       2.87 → 3.69 GB available
```

### 四、这一轮的一句话

> 有些工作不产生代码，但决定了"能不能交代清楚"。

> **代码是给机器的，差异账本是给人的。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 369 轮（新增 `docs/DEVIATIONS.md` 差异账本；关掉原版进程把 available 从 2.87 GB 拉回 3.69 GB）。

---

## 差异账本（`docs/DEVIATIONS.md`）

七节：绑定形状(272) · UI 结构 · 文案/URL(inferred) · 不可得(三源否证) · 故意留白 · 类型级缺口(18) · 怎么读。

**判断 1:1 分三层**：行为（最实）→ 结构/文案（次之）→ 形状（有意保留差异）。

## 内存纪律（这轮再次触发）

`available < 4 GB` 时：不做变异测试（29 轮编译）、不跑完整套件，只跑文档守卫（57 个）。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过（上一轮跑过）
缺口       17（名字级）/ 18（类型级）
原版进程   已关闭（需要 GUI 核对时再启动）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
