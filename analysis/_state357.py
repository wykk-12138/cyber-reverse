import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 357 轮：`MessageBoxDialog.Type` / `ProfileCsvEditorView.GroupName`（缺口 34 → 32）

### 一、这回先读类，再动手

按 §12 先 `grep 'class X' -Context 0,16`：

- `MessageBoxDialog` 构造**本来就收** `MessageBoxType type` —— 所以绑定成员 `Type` 应该是那个枚举，
  我第一次写成 `string`（猜的），编译过了但语义不对，测试一构造函数就暴露出来；
- `ProfileCsvEditorView` 有 `private readonly ComboBox _group`，`GroupName` 只需暴露所选值。

### 二、两次修正都来自"读了真实代码"

1. `Type` 从 `string` 改为 `MessageBoxType`，并由构造函数赋值（`Type = type;`）；
2. 测试不再 `new MessageBoxDialog(...)` —— **Window 在没有 Avalonia 平台时构造会抛**
   （`Unable to locate 'Avalonia.Platform.IWindowingPlatform'`），改为纯反射断言。

### 三、验证

```
DialogFieldTests   2 通过
完整套件           1525 通过 / 0 失败 / 2 跳过
bind_scope         34 → 32
```

### 四、这一轮的一句话

> 两次修正都不是"想明白了"，而是"读到真相了"：一个枚举名，一个平台限制。

> **猜对和读对，在代码里长得一样；区别只在下一次编译。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 357 轮（`MessageBoxDialog.Type` = `MessageBoxType`；`ProfileCsvEditorView.GroupName`；缺口 32）。

---

## 测试上的硬限制（记住）

**`Window` 在没有 Avalonia 平台时无法构造**：`new MessageBoxDialog(...)` 会抛
`Unable to locate 'Avalonia.Platform.IWindowingPlatform'`。
→ 涉及 `Window` 的绑定成员，测试只能用**反射**断言，不能构造实例。

`UserControl`（如 `TaskDetailsView`、`ProfileCsvEditorView`）可以构造，`Close()` 无宿主时返回 false。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 32（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
