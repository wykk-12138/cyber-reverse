import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 367 轮：把"成员形状"变成一个工具 + 一份账本

### 一、线索的来源

上一轮在池子里看到 `GoogleAccountsView,Cybersole.Add!Getter` 这类字符串 ——
它们不是普通字符串，而是**编译期绑定产生的访问器名**。既然存在，就可以系统提取。

### 二、新工具 `tools/bind_shape.py` + 新账本 `docs/BINDING_SHAPES.md`

```
102 个类型在池子里有访问器证据
```

每个绑定成员现在都有"形状"：

| 形状 | 含义 |
|---|---|
| `Getter,Property,Setter` | **可读写属性** —— 用户动作多半是 `ICommand` 属性 |
| `Getter,Property` | **只读属性** —— 数据 |
| `—` | 池子里没有该成员的访问器证据（可能写成方法） |

### 三、立刻用上：`AccountGroupView.GroupName`

账本说它有 `Setter`，而我写成只读。已改为**可写**（写入同时更新输入框与组名），
并在注释里指向 `docs/BINDING_SHAPES.md`。

### 四、验证

```
完整套件   1525 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 前几轮我一直在**猜形状**（方法还是属性、只读还是可写）；这一轮发现：**池子早就写了答案，102 次。**

> **"没有证据"和"没有去找证据"是两件事。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 367 轮（新增 `tools/bind_shape.py` 与 `docs/BINDING_SHAPES.md`：102 个类型的成员形状）。

---

## 新账本：成员形状

```
python tools/bind_shape.py [过滤词]
docs/BINDING_SHAPES.md        ← 102 个类型 × 每个绑定成员的 Property/Getter/Setter
```

| 形状 | 含义 | 写法 |
|---|---|---|
| `Getter,Property,Setter` | 可读写属性 | 用户动作 → `ICommand` 属性；数据 → 可写属性 |
| `Getter,Property` | 只读属性 | 数据 |
| — | 无访问器证据 | 可能是方法 |

**已应用**：`AccountGroupView.GroupName` 改为可写（证据有 `Setter`）。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
