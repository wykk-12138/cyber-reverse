import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 396 轮：TaskGroup 文案清零，并且**真的接到了界面上**

### 一、十条原文

`Captcha Solving Source` · `Select source` · `Cloudflare Solver` · `Monitor Delay` · `Error Delay` ·
`When toggled, both monitor and retry delays will stay the same` · `Resetting at` ·
`Total Checkout Limit` · `Webhook Filter` · `Select webhook(s)`

### 二、这一轮和前三轮的区别

前三轮（Accounts / Proxies / Tasks / Profiles）我加的是**常量**，界面上的字还没换。
这一轮**把标签真的接到了常量上**：

```csharp
UiKit.Row(MonitorDelayLabel, monitor),     // 原来是 "Monitor delay (ms)"
UiKit.Row(ErrorDelayLabel, retry),         // 原来是 "Retry delay (ms)"
```

顺带发现一件有意思的事：原版的 "Error Delay" 字段**对应的模型字段是 `retryDelay`**
（备份里没有 errorDelay）—— 我把它标成 `Retry Delay` 的第三个框保留，但注释写清了这个错位。

### 三、一次自己造的坑

第一版替换把 `TaskCreatorView` 里的同名行也改了（同名 `UiKit.Row("Monitor delay (ms)", …)`
在两个类里都有）→ `CS0103`。改成**先断言每一行的当前内容，再按行号改**，才对准。

```
完整套件   1574 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 加常量不是目的，**换掉界面上的字才是**。

> **"定义对了"和"用上了"之间，隔着一次真正的替换。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 396 轮（TaskGroup 文案清零，并把 delayer/limits/captcha/notifications 的标签真的接上）。

---

## 文案清零的五个区域

| 区域 | 条数 | 轮次 | 是否接到界面 |
|---|---|---|---|
| Accounts | 10 | R392 | 常量（待接线） |
| Proxies | 6 | R393 | 常量（待接线） |
| Tasks | 10 | R394 | 常量（待接线） |
| Profiles | 13 | R395 | 常量（待接线） |
| **TaskGroup** | **10** | **R396** | **已接线** |

**下一步**：把前四个页面的常量替换到实际控件上（照 R396 的做法：先断言原行内容，再按行改）。

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
