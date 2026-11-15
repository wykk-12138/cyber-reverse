import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 329 轮：**真的开了 GUI**，复核设置页导航栏 —— 四件事全部对上

### 一、这次是实机（不是记忆）

原版 `target\\Cybersole.exe`（5.18.32）**保留会话**直接进主界面，点 Settings 后读到导航栏：

```
Version 5.18.32   CHECK FOR UPDATES
──────────────────────────
General（选中） Appearance Notifications Webhooks Email Accounts
Google Accounts PayPal Accounts Data
────────────
ADVANCED              ← 灰、不可点的小标题
────────────
Captcha Providers Cloudflare Providers Keyboard Shortcuts
Custom Stores Custom Sizes Payment
────────────
Need Help?   Log Out（红）
```

### 二、四件事被确认

1. **`ADVANCED` 是标题不是页面** —— R300 的守卫写对了；**R312 我加"第 16 个页面"时被它拦下，也是对的**。
   这一次是用眼睛（和截图）确认的，不是靠注释。
2. **顺序与复刻件 `Sections` 完全一致**。
3. **底部 `Log Out` 存在**，复刻件已有（`Auth.SignOut()`）。
4. **General 页的行一致**：Language / Default Monitor·Error·Timeout（2.500 ms、2.500 ms、10 sec）/
   ATC Browser Proxy·Queue Presentation（None / Time remaining）/ Monitor Concurrency（Maximum + 3 max）/
   Startup Page（Home）/ Currency（USD）。

### 三、结论

**设置页这块不需要改** —— 结构、顺序、文案、控件值都对得上。
这条结论与"我读代码觉得对"不同：**它来自运行中的原版**。

### 四、验证

```
原版进程 pid 14248，窗口 1429×892（与 GUI_GEOMETRY 记录一致）
复刻件全套   1478 通过 / 0 失败 / 2 跳过（R328）
```

### 五、这一轮的一句话

> 这是我这一程第一次**不是"读"而是"看"**着原版做交叉验证 —— 而且它验证的正好是我前几轮最没底的那条。

> **守卫拦下我的那一次（R300），这一轮拿到了实物证据。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 329 轮（**实机复核设置页导航**：ADVANCED 是标题、顺序一致、Log Out 在底部、General 行一致）。

---

## 实机 GUI 复核结论（`docs/GUI_BASELINE.md` R329 节）

原版 `target\\Cybersole.exe` 保留会话启动（pid 14248，窗口 1429×892），Settings 导航栏逐项对照：

| 项 | 结论 |
|---|---|
| `ADVANCED` | **灰色不可点的小标题**，不是页面 → R300/R312 的守卫是对的 |
| 导航顺序 | 与复刻件 `Sections` **完全一致** |
| `Log Out` | 底部红色项，复刻件已有（`Auth.SignOut()`） |
| General 行 | Language / Default Monitor·Error·Timeout / ATC Browser Proxy / Queue Presentation / Monitor Concurrency / Startup Page / Currency —— 全一致 |

**设置页不需要改动。**

## 状态

```
完整套件   1478 通过 / 0 失败 / 2 跳过（R328）
缺口       17（real = ceiling）
mutation   29 / 29 fired（R328）
Commit     15.9 GB / 可用 18.9 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
