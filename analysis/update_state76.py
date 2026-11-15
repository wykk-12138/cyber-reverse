import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 75 轮。", "最后更新：第 76 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **826 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **832 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R75）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R76）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

anchor = "- **一个数字有两个来源"
add = '''- **`t.find(x)` 回答的是「x 第一次在哪」，不是「我要的那个 x 在哪」。** R76 的改写脚本用
  `find('Content = UiKit.Scroll(UiKit.Form(')` 定位，命中的是 `GeneralSettingsView` 的那一行，
  于是从那里到目标注释之间的 **600 行被替换掉**：AppearanceView、NotificationsView、
  KeyBindsView 整个没了，本仓库没有 git、没有备份目录。
  **补得回来是因为 R74/R75 一轮一轮抄过那三页的文字——那是唯一的备份。**
  重写脚本时用「两段唯一锚点 + assert 都在同一函数内」，或者先 grep 出全部出现位置。
- **只写状态行、什么都不打开的按钮/菜单项'''
if anchor in t and add not in t:
    t = t.replace(anchor, add, 1)
    print("trap added")
else:
    print("trap anchor missing or already present")

# A second known flake for the live TLS probe.
old2 = "- **`TheSecureTokenRotatesWithinSeventySeconds` 偶发红**"
new2 = '''- **`own TLS 1.2 + HTTP/2` 偶发红**（R76 见过一次：`proto=http/1.1 transport=` 、334 bytes）。
  单独跑 `dotnet run --project tools\\TlsProbe.Cli -c Release -- --own example.com` 必过
  （`proto=h2 transport=own-tls12 alpn=h2`、577 bytes）。是 harness 抓输出的问题，不是回归。
- **`TheSecureTokenRotatesWithinSeventySeconds` 偶发红**'''
if old2 in t:
    t = t.replace(old2, new2, 1)
    print("flake note added")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
