import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 78 轮。", "最后更新：第 79 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **842 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **847 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R78）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R79）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

anchor = "- **界面上的每个控件都要能指出「另一端接着谁」。**"
add = '''- **「不在屏幕上」≠「不在逻辑树里」。** Avalonia 用 `IsVisible=false` 让控件消失，它仍然是子节点。
  断言「空态消失」必须走祖先链找 `IsVisible=false`（R79 一条断言写错三次），
  而且 `IsVisible` 标在**包着它的容器**上，不在文字本身。
- **能干活不等于一样。** R79 把 replica 自己那套「表单摊在页面上」的 Custom Stores 删了，
  换成原版的「表 + 弹窗」。功能没变、形状变了——这才是 1:1 的标准。
- **界面上的每个控件都要能指出「另一端接着谁」。**'''
if anchor in t and "「不在屏幕上」≠「不在逻辑树里」" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
