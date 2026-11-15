import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 355 轮：`Close` / `OpenUrl` 家族 —— 一次补五处，类型级缺口 40 → 37

### 一、补了什么

| 类型 | 成员 | 语义 |
|---|---|---|
| `UserView` | `OpenUrl` | 开浏览器；三个链接（Dashboard / ToS / Privacy）改为调用它，不再只写状态栏 |
| `TaskDetailsView` | `Close` | 关宿主窗口 |
| `TaskCreatorView` | `Close` | 同上 |
| （R354 已补）`TaskGroupView` | `Close` | 同上 |

### 二、统一的实现形状

```csharp
public bool Close()
{
    if (TopLevel.GetTopLevel(this) is not Window host) return false;
    host.Close();
    return true;
}
```

返回 `bool` 是刻意的：**没有窗口时返回 false**，这样"无宿主构造"的测试能断言，而不是只能看它不崩。

### 三、验证

```
CloseAndOpenFamilyTests   3 通过
完整套件                  1521 通过 / 0 失败 / 2 跳过
bind_scope                40 → 37
```

### 四、这一轮的一句话

> 同一段 `Close` 我写了三次。**没有抽成基类**，因为这些类分属三个不同文件、基类各不相同（`UserControl` 与
> `Window` 混排），抽基类的风险大于三份十行代码。

> **重复十行可以接受，为了"优雅"动一次继承树不行。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| `TaskGroupView` | `CloudflareSolvers` / `Close`（R354，**该类型绑定成员清零**） |',
                '| `TaskGroupView` | `CloudflareSolvers` / `Close`（R354，**该类型绑定成员清零**） |\n| `UserView` | `OpenUrl`（R355，三个链接改为真开浏览器） |\n| `TaskDetailsView` / `TaskCreatorView` | `Close`（R355） |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('backlog updated')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 355 轮（`Close`/`OpenUrl` 家族补五处；类型级缺口 40 → 37）。

---

## `Close` / `OpenUrl` 的约定（今后照此写）

```csharp
public bool Close()   // 无宿主窗口 → false
public static bool OpenUrl(string url)   // 无法启动浏览器 → false
```

两处都**返回 bool**，让"无宿主/无浏览器"可断言。

已覆盖：`UserView.OpenUrl`、`TaskGroupView.Close`、`TaskDetailsView.Close`、`TaskCreatorView.Close`、`HelpView.OpenUrl`。

## 状态

```
完整套件   1521 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 37（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
