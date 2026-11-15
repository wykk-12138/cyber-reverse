import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_SHAPES.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## 系统差异：273 个"动作"成员，原件是属性、复刻件是方法（R368）

`python tools/shape_audit.py` 会列出所有"池子说有 Setter、而复刻件不是可写属性"的成员：

```
members with accessor evidence : 465
  settable                     : 327
  getter-only                  : 138
mismatches（可写证据 vs 复刻件写法）: 273 → 273（修 ComboBoxEdit 两条后 272）
```

### 这是什么差异

原件的 XAML 用 `Command="{Binding Xxx}"` 绑动作，所以**每个动作都是 `ICommand` 属性**；
复刻件用手写控件树，动作就是方法。**行为等价，形状不同。**

### 为什么不在这一轮全改

- 复刻件**没有任何 XAML 绑定**，形状差异不影响运行；
- 273 处全改成 `ICommand` 属性是纯形式重构，风险大于收益（R352 的教训还热着）。

### 规则（已写入 METHOD §13）

**新增"用户动作"成员时，写成 `ICommand` 属性**（与原件同形），存量不动。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('BINDING_SHAPES notes added')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 368 轮：把"形状差异"量化并定性（273 处，决定不改）

### 一、新工具：`tools/shape_audit.py`

它把两件事对起来：

- **池子**：成员有没有 `Setter` 证据；
- **复刻件**：该成员是可写属性、只读属性，还是方法。

### 二、结果

```
有访问器证据的成员 465（可写 327 / 只读 138）
"有 Setter 证据但复刻件不是可写属性"   273 → 272（修了 ComboBoxEdit 两个命令属性）
```

**273 处不是 273 个 bug，而是一个系统差异**：原件用 XAML `Command=` 绑动作，
所以动作都是 `ICommand` 属性；复刻件手写控件树，动作就是方法。

### 三、决定：存量不改

- 复刻件没有任何 XAML 绑定，形状不影响运行；
- 273 处全改是纯形式重构，风险大于收益（R352 切坏文件的教训就在昨天）。

**新规则**：新增动作成员写成 `ICommand` 属性（与原件同形）；存量保留方法。

### 四、验证

```
完整套件   1525 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 有些差异应该修，有些差异应该**被量化之后放过** —— 关键在于说清"为什么不修"。

> **不是所有不一致都是缺陷；但所有不修都必须有理由。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 368 轮（新增 `tools/shape_audit.py`；量化出 273 处形状差异，**决定不改**并记录理由）。

---

## 一个已知且被接受的差异

```
有访问器证据的成员 465（可写 327 / 只读 138）
形状不一致       273 → 272   （"池子说可写，复刻件是方法"）
```

原因：原件用 XAML `Command=` 绑动作（动作=属性），复刻件手写控件树（动作=方法）。
**行为等价，形状不同**。存量不改；新增动作成员按 §13 写成 `ICommand` 属性。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
