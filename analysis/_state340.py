import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R340：Webhook 提交按钮是**三态机**（实机逐个走过）

在实机上把三个状态都走了一遍：

| 状态 | 按钮文字 | 是否可点 |
|---|---|---|
| Name 空 | **`Enter name`** | 否（灰） |
| Name 有值、URL 空 | **`Enter valid webhook`** | 否（灰） |
| Name 有值、URL 合法 | **`Save`** | **是（绿）** |

同时确认：**选定 `Discord` 之后没有多出任何字段** —— `Extra Fields` / `Events` / `Attach to group`
都没有出现（这直接质疑 R318 按 locale key 加的 `ExtraFields`：它在界面上没见过）。

### 复刻件改动

`WebhookCreatorView` 整类重写（含 R339 的布局）：`SubmitLabel(name, url)` / `IsWebhookUrl(url)` 两个纯函数 +
footer 按钮跟随两个输入框实时换字与启停。

### 一次自己造的乌龙

测试里我先写了 `("probe", "https://discord.com/api/webhooks", "Enter valid webhook")` —— 失败。
原因：那串 URL 在实机上是**占位水印**，不是值；输入框实际是空的。
**把水印当成值**，是我这一轮最典型的误读。

### 三次编辑失败的过程也要记

这一轮我在同一个 ctor 上改了三次都编译不过（索引错位、误伤到隔壁 `BrowserDriverCreatorView`、
把注释行并进了上一行）。最后**整类重写**才干净通过。

> 教训：**在别人（哪怕是自己）写的长文件里做索引级外科手术，代价远高于整段重写。**
> 下一次直接重写，不要省那几分钟。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 340 轮：Webhook 提交按钮的三态机 + 一次漫长的自伤

### 一、实机把三个状态都走了一遍

| 状态 | 按钮 | 可点 |
|---|---|---|
| Name 空 | `Enter name` | 否 |
| Name 有、URL 空 | `Enter valid webhook` | 否 |
| Name 有、URL 合法 | `Save`（绿） | **是** |

**顺带否证**：选定 `Discord` 后**没有**多出任何字段 —— `Extra Fields` / `Events` / `Attach to group` 都没出现。
这让 R318 依据 locale key 加的 `ExtraFields` 变成"界面未证实"。

### 二、复刻件

`WebhookCreatorView` 整类重写：`SubmitLabel(name, url)` / `IsWebhookUrl(url)` 两个纯函数，
footer 按钮跟着两个输入框实时换字与启停；R339 的布局保留。

### 三、两次错误都值一句话

1. **把水印当值**：测试里我写了 `("probe", "https://discord.com/api/webhooks", "Enter valid webhook")` ——
   那串 URL 在实机上是**占位水印**，输入框实际是空的。失败后改正。
2. **索引级外科手术**：同一个 ctor 我改了三遍都编译不过（错位、误伤隔壁类、注释并行），
   最后**整类重写**才通过。

> **在长文件里做索引级修改，代价远高于整段重写 —— 下次直接重写。**

### 四、验证

```
WebhookCreatorLabelTests   6 通过
完整套件                   1500 通过 / 0 失败 / 2 跳过
```
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 340 轮（Webhook 提交按钮三态机落地；`Extra Fields` 在实机**未出现**）。

---

## 这一轮的两个结论

1. **提交按钮是三态机**（实机走过）：`Enter name` → `Enter valid webhook` → `Save`（仅最后一态可点）。
   已实现为 `WebhookCreatorView.SubmitLabel` + `IsWebhookUrl`，6 条测试。
2. **选定 `Discord` 后没有多出字段** → R318 依 locale key 加的 `IWebhook.ExtraFields`
   **在界面上未证实**，标注待查（不删，但不再当作"有界面依据"）。

## 教训（写进 `docs/GUI_BASELINE.md`）

- 把**水印当值**导致一条测试写错；
- 在长文件里做**索引级外科手术**改了三次都不过，最后整类重写才干净 —— **下次直接重写**。

## 状态

```
完整套件   1500 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     26 GB / 可用 13 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
