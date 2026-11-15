import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 73 轮。", "最后更新：第 74 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **803 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **809 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R73）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R74）。"),
    ("目标          原版 Cybersole 5.18.30（NativeAOT，123 MB）",
     "目标          原版 Cybersole 5.18.30（NativeAOT，123 MB，FileVersion 5.18.30.0）"),
]

for old, new in subs:
    if old not in t:
        print("skip (already applied?):", old[:44])
        continue
    t = t.replace(old, new, 1)

# Settings walk result goes into the remaining-work list.
old_next = """3. **继续 GUI 走查没点过的页**：`Settings → Data`、`Settings → Advanced → Captcha Providers`、
   `Settings → Webhooks`。这三页一个都没点过。"""
new_next = """3. **Settings 剩下的页**（R74 点了 General / Data / Webhooks / Captcha Providers，剩 11 页没点）：
   Appearance / Notifications / Email Accounts / Google Accounts / PayPal Accounts /
   Cloudflare Providers / Keyboard Shortcuts / Custom Stores / Custom Sizes / Payment / Need Help?。
   页头机制已就位（`SettingsShell.PageHeaders`），**点一页填一行**。
4. **两个空态**：`Captcha Providers` 和 `Webhooks` 在「一个都没有」时，原版只显示
   `Add Source` / `New Webhook` + 两行空态；replica 直接摆出列表和表单。不是错，是空态没做。"""
if old_next in t:
    t = t.replace(old_next, new_next, 1)
    print("next-step updated")
else:
    print("next-step anchor not found (left as is)")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
