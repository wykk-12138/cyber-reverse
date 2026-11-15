import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 359 轮：`SolverWindow.Minimise` / `Dispose`（类型级缺口 29 → 28）

### 一、按 §12 先读

`SolverWindow : Window` 有 `_services` / `_settings` / 队列与三个输入框，没有 `Minimise` / `Dispose`。

### 二、补的两个

```csharp
public void Minimise() => WindowState = WindowState.Minimized;
public void Dispose() => Close();
```

### 三、一次"想当然"的修正

我先写成 `public new void Dispose() { Close(); base.Dispose(); }` —— **编译报错：
`Window` 没有 `Dispose`**。Avalonia 的 `Window` 自己不实现 `IDisposable`，所以这里不该 `new` + `base`。
改成一条 `Close()` 路径，注释写明"绑定的名字就是唯一释放路径"。

> 这又是 §12 的延伸：**不仅字段要读，基类的接口也要读**。

### 四、验证

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 29 → 28
```

### 五、这一轮的一句话

> "既然是 Window，那它一定有 Dispose" —— 这句想当然，被编译器一句话否掉了。

> **基类也要读，不能只读自己的字段。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §12.1 读类的时候，连基类一起读（R359）

`SolverWindow : Window` 我写了 `public new void Dispose() { … base.Dispose(); }`，
编译报 **`Window` 没有 `Dispose`** —— Avalonia 的 `Window` 不实现 `IDisposable`。

规则补一条：**加成员前，除了字段和构造，还要看一眼基类提供了什么**（有没有同名成员、是不是接口实现）。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §12.1 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 359 轮（`SolverWindow.Minimise` / `Dispose`；类型级缺口 28）。

---

## 一条新补的纪律（`docs/METHOD.md` §12.1）

**加成员前连基类一起读**：`Window` 没有 `Dispose`，写 `new` + `base.Dispose()` 直接编译失败。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 28（类型级，起点 52）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
