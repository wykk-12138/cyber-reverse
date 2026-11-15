import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 74 轮。", "最后更新：第 75 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **809 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **826 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R74）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R75）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

old_next = """3. **Settings 剩下的页**（R74 点了 General / Data / Webhooks / Captcha Providers，剩 11 页没点）：
   Appearance / Notifications / Email Accounts / Google Accounts / PayPal Accounts /
   Cloudflare Providers / Keyboard Shortcuts / Custom Stores / Custom Sizes / Payment / Need Help?。
   页头机制已就位（`SettingsShell.PageHeaders`），**点一页填一行**。
4. **两个空态**：`Captcha Providers` 和 `Webhooks` 在「一个都没有」时，原版只显示
   `Add Source` / `New Webhook` + 两行空态；replica 直接摆出列表和表单。不是错，是空态没做。"""

new_next = """3. **Settings 十五页的正文**（页头全部齐了，R75 扫完）。**页头只是第一行**，
   每一页的控件清单还差：Notifications 的五个 tab（Checkout / Decline / Captcha / Smart Actions /
   Other）、Keyboard Shortcuts 的快捷键表（Tasks/New Group `Ctrl G`、Task Creator `Ctrl N`、
   Task Editor `Ctrl E`、Start All `F1`、Stop All `F2`、Delete Selected `Delete`、
   Clone Selected `Ctrl …`）、Payment 的三段（3D Secure / External Browser / Browser Profiles）。
   这些都抓到了文字，**还没一条一条对进 replica**。
4. **几处空态**：`Captcha Providers` / `Webhooks` / `Custom Stores` / `Custom Sizes` 在
   「一个都没有」时，原版只显示新建按钮 + 两行空态；replica 直接摆出列表和表单。
   不是错，是空态没做。"""

if old_next in t:
    t = t.replace(old_next, new_next, 1)
    print("next-step updated")
else:
    print("next-step anchor missing")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
