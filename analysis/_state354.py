import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 354 轮：`TaskGroupView` 的绑定成员清零

### 一、补上最后两个

| 成员 | 做法 |
|---|---|
| `CloudflareSolvers` | 成为属性（`_services.Captcha.Registry.Configs` + `DefaultIfEmpty("(none)")`），**Combo 改为读它** |
| `Close` | 关宿主窗口；没有窗口时返回 false（测试里就是这样构造的） |

`bind_scope.py`：`TaskGroupView` 从缺 4 → 缺 2 → **缺 0**（类型级缺口 41 → 40）。

### 二、一条守卫红了，改的是守卫不是代码

`SettingsStorageLinkTests.TheTaskGroupDropdownStillReadsTheCaptchaRegistry` 原来断言
"文件里出现 `_services.Captcha.Registry.Configs`，且其后 600 字符内有 `CloudflareSolver`"。
我把读取搬进了属性，字面断言自然失败 —— **但它要保护的行为没变**：

```csharp
Assert.Contains("UiKit.Combo(CloudflareSolvers)", text);            // 组合框读绑定属性
Assert.Contains("_services.Captcha.Registry.Configs", propertyBody); // 属性读注册表
Assert.Contains("CloudflareSolver", window);                          // 仍写回组字段
```

**三条一起，保护的还是"下拉不是硬编码副本"这件事。**

### 三、验证

```
TaskGroupViewTests   3 通过
完整套件             1518 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 守卫变红时，先问"它保护的行为还在不在"，再决定改谁。

> **行为还在、结构变了 → 改守卫；行为变了 → 改代码。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| `HelpView` | `OpenUrl`（R346，本地函数 → 成员） |',
                '| `HelpView` | `OpenUrl`（R346，本地函数 → 成员） |\n| `TaskGroupView` | `CloudflareSolvers` / `Close`（R354，**该类型绑定成员清零**） |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('backlog updated')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 354 轮（`TaskGroupView` 绑定成员清零：`CloudflareSolvers` 成属性、`Close` 补上；类型级缺口 40）。

---

## 类型级缺口：40（起点 52）

| 已清零的类型 | 轮次 |
|---|---|
| `IWebhook` | R342 |
| `LoginControl` | R343 |
| `HelpView` | R346 |
| `CustomStoresView` / `CustomSizesView`（除 `View`） | R347 |
| **`TaskGroupView`** | **R354** |

## 一条守卫的处置（值得记住）

`TheTaskGroupDropdownStillReadsTheCaptchaRegistry` 因结构变化变红 ——
**行为没变，所以改守卫**，并把它拆成三条断言（组合框读属性 / 属性读注册表 / 字段仍被写回）。

## 状态

```
完整套件   1518 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 40（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
