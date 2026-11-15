import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R339：Webhooks 页 + 「New Webhook」弹窗 —— 实机读到，改了三处、记了三条

### 页面（空态）

```
Webhooks — Receive real time notifications into your favorite services
[ New Webhook                            + ]
                Nothing to see here
                Add some webhooks to get started
```

### 弹窗「New Webhook」

```
+  New Webhook                                    [×]
Name                          Platform
[Personal server      ]       [Select provider  ▾]
Webhook
[https://discord.com/api/webhooks              ]
[            Enter name                         ]
```

### 改了什么（复刻件 `WebhookCreatorView`）

| 项 | 实机 | 改前 | 现在 |
|---|---|---|---|
| 标题 | `New Webhook` | `New webhook` | `New Webhook` |
| Name 占位 | `Personal server` | `Checkout notifications` | `Personal server` |
| URL 占位 | `https://discord.com/api/webhooks` | `…/api/webhooks/…` | 实机原文 |
| Platform 占位 | `Select provider` | 直接列 `Discord/Custom` | 首项 `Select provider` |
| 布局 | Name 与 Platform **同一行**，URL 在 `Webhook` 标题下 | 三行竖排 | 同实机 |

### 记下来但**没改**的三条（证据不足）

1. **提交按钮**：实机空名时显示 `Enter name`（不是 `Save`）。想改成"名字空→`Enter name`、有名字→`Create`"，
   但那要重排 ctor，改到一半编译不过，**已回滚**，只记录；下轮用完整重写方式做。
2. **`Attach to group` / `Events` 两行**：实机在未选 Platform 时**看不到**，但可能在选完之后出现 —— 未验证，保留。
3. **`Extra Fields`**（R318 依照 locale key 加的）：这个弹窗里**没有**。可能属于某个具体 Platform 的展开项，
   也可能只存在于 locale 而没有界面 —— 未定，标注待查。

> 这一轮的教训：**"看到了差异"和"改得动"是两件事。** 记录也要算产出，硬改到编译不过不算。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 339 轮：Webhook 弹窗 —— 改了三处，记了三条，**回滚了一次**

### 一、实机弹窗

```
New Webhook                                        [×]
Name                        Platform
[Personal server    ]       [Select provider  ▾]
Webhook
[https://discord.com/api/webhooks                ]
[              Enter name                         ]
```

### 二、改成的（`WebhookCreatorView`）

标题 `New webhook → New Webhook`；Name 占位 → `Personal server`；URL 占位 → 实机原文；
Platform 首项 → `Select provider`；**Name 与 Platform 同一行，URL 在 `Webhook` 标题下**。

### 三、三次"看到了但没改"

1. **提交按钮**：实机空名时是 `Enter name`。我改到一半（要重排 ctor）编译不过，**已回滚**，只记录；
2. `Attach to group` / `Events`：未选 Platform 时实机看不到，**未验证**是否随后出现，保留；
3. **`Extra Fields`**（R318 按 locale key 加的）：**这个弹窗里没有** —— 可能是某 Platform 的展开项，
   也可能只有文案没有界面。标注待查。

### 四、这一轮的教训

> **"看到了差异"和"改得动"是两件事。** 记录也算产出；硬改到编译不过不算。

回滚后：

```
完整套件   1493 通过 / 0 失败 / 2 跳过
```
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 339 轮（Webhook 弹窗按实机改了标题/占位/布局；`Enter name` 按钮**回滚**并记录）。

---

## 实机核对第十个面：Webhooks + New Webhook 弹窗

已改：标题 `New Webhook`、Name 占位 `Personal server`、URL 占位原文、Platform 首项 `Select provider`、
**Name 与 Platform 同一行 + URL 在 `Webhook` 标题下**。

记录未改（证据不足）：
1. 空名时提交按钮实机是 **`Enter name`**（改写需重排 ctor，本轮回滚）；
2. `Attach to group` / `Events` 未验证是否随 Platform 出现；
3. **`Extra Fields` 在该弹窗里没有** —— R318 的依据只是 locale key，待查。

## 状态

```
完整套件   1493 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     24.5 GB / 可用 14 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
