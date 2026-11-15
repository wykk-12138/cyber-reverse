import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 77 轮。", "最后更新：第 78 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **836 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **842 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R77）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R78）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

anchor = "- **原版的下拉框在 UIA 里没有 peer。**"
add = '''- **界面上的每个控件都要能指出「另一端接着谁」。** R78 查出 Notifications 页的 Sounds 开关、
  声音文件、以及页面级的 `settings.notifications` **全都没有读者**：`NotificationService`
  只弹窗、记日志、发 webhook，从不播放。现在有 `ISoundPlayer`（winmm `PlaySound`，无 NuGet）、
  `NotificationService.PlaySound`，`PublishAsync` 按 `Notifications → Enabled → Sound → Path` 逐层判。
- **开关（ToggleSwitch）不是复选框（CheckBox）。** 原版这一页每行都是右侧绿色开关；
  用 `UiKit.Check` 是不同控件、不同位置。`UiKit.Switch(caption, value, onChanged)` 是对的形状，
  而且文字是 `TextBlock`，测试能扫到。
'''
if anchor in t and "界面上的每个控件都要能指出" not in t:
    t = t.replace(anchor, add + anchor, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
