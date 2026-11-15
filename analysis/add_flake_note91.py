import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

anchor = "- **跑测试前先清 `testhost`。**"
add = """- **`-Full` 下 Analytics/Chart 一组 UI 测试会偶发红，而同样命令单跑必过。** R91 连撞三次
  （CheckoutStatsPeriodTests / AnalyticsAndModalTests / ChartTimelineTests，每次不同一条），
  清 `testhost` 后重跑 `-Full` 全绿。**是本机运行期噪音，不是回归**；判断方法永远是
  单跑该条 + 清进程重跑整轮。
- **跑测试前先清 `testhost`。**"""

if anchor not in t:
    raise SystemExit("anchor missing")
if "-Full` 下 Analytics/Chart" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add, 1))
    print("flake note added")
