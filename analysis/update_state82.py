import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 81 轮。", "最后更新：第 82 轮。"),
    ("**859 通过 / 0 失败 / 2 跳过**", "**864 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R81）。", "上一次跑：全 PASS（R82）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

anchor = "- **`scroll` 对这一层 Avalonia 窗口无效**"
add = '''- **原版会掉回登录页。** R82 打开时窗口已关、进程已无；重启后停在 `Cybersole.exe … "Login"`。
  **没有凭据就没有 Settings**，GUI 这一路证据当场失效。所以：**能落成文字快照 + 断言的
  东西要尽早落**（R74–R81 抄下的字符串，现在就是「原版再打不开也还在」的东西）。
- **视图类普查是免费的函数数量口径。** 二进制 Avalonia 资源清单的
  `ClassToResourcePathIndex` 有 **87 条**（类名 + .axaml）。快照存 `docs/original_view_classes.txt`；
  实测 **69 同名 / 12 改名合并 / 6 真没有**（`SplashWindow`、`LoginControl`、`CustomBrowser`、
  `EmptyView`、`GroupGrid`、`ProxyCreatorView`）。守卫在 `OriginalViewClassParityTests`，
  欠账清单只准变短。
- **同一个对话框可能有两份实现。** 资源清单里有 `Settings/Modals/StoreCreatorView.axaml` 与
  `SizeCreatorView.axaml`，而 replica 的 `SettingsModals.cs` 早就有 `StoreCreatorView` ——
  R79/R80 在 `CustomStoresView`/`CustomSizesView` 里手搭的同名弹窗是**第二份**。
  下一轮先让手搭的那两个改为使用已有类。
- **`scroll` 对这一层 Avalonia 窗口无效**'''
if anchor in t and "原版会掉回登录页" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
