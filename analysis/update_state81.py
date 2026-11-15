import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 80 轮。", "最后更新：第 81 轮。"),
    ("**852 通过 / 0 失败 / 2 跳过**", "**859 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R80）。", "上一次跑：全 PASS（R81）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

anchor = "- **同一个 Settings 页面对了之后"
add = '''- **`scroll` 对这一层 Avalonia 窗口无效**（后台上报 `Background delivery is not available … mouse_scroll`）。
  必须给**列表内的像素坐标 + foreground**：`app.scroll([900,700], "down", 4, {delivery_mode:"foreground"})`，
  否则滚轮事件被丢掉，列表一动不动而你以为是「到底了」（R81 一开始就因此少收了 3 条）。
- **整份数据做完不等于功能做完。** R81 发现 `ErrorCatalog` 里躺着 13 条逐字抄来的错误说明，
  而 `HelpView` 的注释写着「没有错误索引可搜」—— **一份没人渲染的目录，和一份没写过的目录，
  在屏幕上完全一样。**
- **`ChartTimelineTests.AnalyticsViewOffersFourCharts` 偶发红**（R81 的 `-Full` 见过一次，单跑必过，
  重跑 `-Full` 全绿）。属于共享 UI 状态的偶发，不是回归。
- **同一个 Settings 页面对了之后'''
if anchor in t and "`scroll` 对这一层 Avalonia 窗口无效" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
