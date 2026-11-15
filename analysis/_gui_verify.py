import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R329：设置页导航栏 —— 实机复核（重启后第一次真正开 GUI）

原版 `D:\\projects\\cyber-reverse\\target\\Cybersole.exe`（5.18.32）以**保留会话**启动，直接进主界面，
点 Settings 后读到导航栏（从左到右、从上到下）：

```
Version 5.18.32    CHECK FOR UPDATES
────────────────────────────────────
General                 ← 选中态（高亮）
Appearance
Notifications
Webhooks
Email Accounts
Google Accounts
PayPal Accounts
Data
────────────
ADVANCED                ← 灰色、不可点的小标题（不是页面）
────────────
Captcha Providers
Cloudflare Providers
Keyboard Shortcuts
Custom Stores
Custom Sizes
Payment
────────────
Need Help?
Log Out                 ← 红色
```

### 这一次复核确认了四件事

1. **`ADVANCED` 确实是标题，不是页面** —— R300 那条守卫
   （`SettingsShellTests.AdvancedIsAGroupCaptionNotAPage`）写的是对的；
   R312 我加"第 16 个页面"被它拦下，也是对的。
2. **顺序与复刻件的 `Sections` 完全一致**（General → … → Payment → Need Help?）。
3. **底部有 `Log Out`** —— 复刻件 `SettingsShell` 已有（`Auth.SignOut()`），一致。
4. **General 页的行也一致**：Language / Default Monitor·Error·Timeout（2.500 ms、2.500 ms、10 sec）/
   Default Profiles·Proxies（None）/ ATC Browser Proxy·Queue Presentation（None、Time remaining）/
   Monitor Concurrency（Maximum + 3 max）/ Startup Page（Home）/ Currency（USD）。

### 结论

设置页这一整块**不需要改动** —— 它是"看起来像"之外的真对齐：结构、顺序、文案、控件值都对得上。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE: settings rail verified')
