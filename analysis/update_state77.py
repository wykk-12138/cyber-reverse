import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 76 轮。", "最后更新：第 77 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **832 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **836 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R76）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R77）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

anchor = "- **`t.find(x)` 回答的是"
add = '''- **原版的下拉框在 UIA 里没有 peer。** `role:combobox` 查不到，像素点击的正确姿势是
  「截图坐标 ÷ (窗口宽/截图宽)」——驱动会把传入值再乘一次缩放（R77 实测 1.1288）。
  即便如此，点中之后**弹层不会出现、也没有新 HWND**。所以「下拉框里有哪些选项」
  这一层证据目前取不到，不要写成「大概是……」。
- **`Enum.GetNames<T>()` 不能直接当界面文案。** R77 屏幕上出现 `RoundRobin`，原版是
  `Round robin`。给枚举字段的页面一律走显式显示名表。
- **`t.find(x)` 回答的是'''
if anchor in t and "Enum.GetNames<T>() 不能直接当界面文案" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("trap anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
