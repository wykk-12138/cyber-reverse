import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 371 轮：`AccountView.CreateGroup` 提取，以及 IDA 通道当前不可用

### 一、先说工具状态（诚实交代）

```
PROXY: MISSING - DSH did not spawn [python -m ida_pro_mcp]
INSTANCE: none - no IDA database loaded, or IDA is not running
PORT 13337: REFUSED
```

按 `AGENTS.md`：这需要**重启 DSH 或重开 IDA+库**才能恢复 —— 两条都会中断当前会话，所以这一轮
**没有走反编译路线**，改用池子 + 现有代码推进，并把"待 IDA 复核"的项继续留在账上。

### 二、补的成员

`AccountView.CreateGroup`：原本是按钮里的内联 lambda（`CreateGroupModal.Show(this, …)`），
提取成成员，按钮改为调用它。

- 第一次插入**插到了构造函数体中间**（`CS0106`），因为我的锚点是按钮那一行，它在 ctor 里；
- 第二次把成员挪到类级别、锚点用 `private Control Build()`，通过。

**教训（第 N 次）**：*在类里插方法，锚点必须是一个方法声明，不能是方法体里的一行。*

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 18 → 17
```

### 三、这一轮的一句话

> 这一轮没有反编译证据可用，我既没有假装有，也没有停工 —— 用池子和现有代码推进了一个成员。

> **工具坏了不要紧，别顺手把"没有证据"写成"有证据"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 371 轮（`AccountView.CreateGroup` 提取；**IDA MCP 当前不可用**，已记录恢复条件）。

---

## 工具状态（影响下轮路线）

```
ida MCP  PROXY MISSING / INSTANCE none / PORT 13337 REFUSED
恢复      重启 DSH 或重开 IDA 并载入库（两者都会中断会话）→ 需要用户在方便时决定
```

在恢复之前：**只做池子/代码内的推进**，需要反编译才能定的项继续留白。

## 新纪律

**在类里插方法，锚点必须是方法声明，不能是方法体里的一行**（R371 因此把成员插进了 ctor）。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 17（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
