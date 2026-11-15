import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 82 轮。", "最后更新：第 83 轮。"),
    ("**864 通过 / 0 失败 / 2 跳过**", "**868 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R82）。", "上一次跑：全 PASS（R83）。"),
    ("UI 类 | **89 个，37 个不可达**", "UI 类 | **89 个，37 个不可达**"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

anchor = "- **原版会掉回登录页。**"
add = '''- **`Window` 子类不能在无头测试里构造。** `new StoreCreatorView(...)` 抛
  `Unable to locate 'Avalonia.Platform.IWindowingPlatform'`。要测这类弹窗，**读源码断言形状**
  （标题常量 / 字段行 / 按钮文案 / 没有 Save-Close），或另建一个 headless 平台。
- **「本来就有」不等于「本来就对」。** R82 说「让手搭弹窗改用已有类」，R83 一看：
  已有的 `StoreCreatorView` 是 Name+URL+Save/Close，`SizeCreatorView` 是 33 个硬编码尺码勾选表
  —— 两个都是自己想的，和原版对不上。**正确动作反过来：把证据搬进旧类，删掉手搭那份。**
  为了「消除重复」而把一个错的实现变成唯一实现，比两份都错更糟。
- **原版会掉回登录页。**'''

if anchor in t and "「本来就有」不等于「本来就对」" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
