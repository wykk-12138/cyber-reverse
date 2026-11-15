import io

base = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests"

# 1) The clone suffix moved with the class: TaskView.cs, not TasksViews.cs.
p = base + r"\CloneNamingTests.cs"
t = io.open(p, encoding="utf-8").read()
old = 'var tasks = Read("src/Cybersole.Ui/Views/Tasks/TasksViews.cs");'
new = ('// R73: the page and its clone call site moved out of the grab-bag file.\n'
       '        var tasks = Read("src/Cybersole.Ui/Views/Tasks/TaskView.cs");')
if old not in t:
    raise SystemExit("clone path anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("clone path fixed")

# 2) Two baseline entries are reachable now.
p2 = base + r"\UnreachedUiTypesTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
old2 = '        "TaskCreatorView", "TaskDetailsView", "TaskGroupListView", "TaskGroupView", "GroupSummary",'
new2 = ('        // R73 wired TaskDetailsView (View Task) and TaskGroupListView (Group Settings), so the\n'
        '        // two came off this list — the guard says so, which is the point of the guard.\n'
        '        "TaskCreatorView", "TaskGroupView", "GroupSummary",')
if old2 not in t2:
    raise SystemExit("baseline anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))
print("baseline updated")

# 3) One more UI class (TaskGrid).
p3 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\PARITY.md"
t3 = io.open(p3, encoding="utf-8").read()
old3 = "**75 个 UI 类：24 个 `Window` 子类 + 51 个 `UserControl` 子类。**"
new3 = "**76 个 UI 类：24 个 `Window` 子类 + 52 个 `UserControl` 子类。**"
if old3 not in t3:
    raise SystemExit("parity count anchor missing")
io.open(p3, "w", encoding="utf-8", newline="").write(t3.replace(old3, new3, 1))
print("parity count updated")

p4 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\mutation-check.py"
t4 = io.open(p4, encoding="utf-8").read()
t4 = t4.replace('"find": "**75 个 UI 类：24 个",', '"find": "**76 个 UI 类：24 个",', 1)
t4 = t4.replace('"replace": "**75 个 UI 类：23 个",', '"replace": "**76 个 UI 类：23 个",', 1)
io.open(p4, "w", encoding="utf-8", newline="").write(t4)
print("mutation anchor updated")

p5 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\VERDICT.md"
t5 = io.open(p5, encoding="utf-8").read()
old5 = "UI 类 | 88 个，**41 个不可达**"
new5 = "UI 类 | 89 个，**39 个不可达**"
if old5 not in t5:
    raise SystemExit("verdict guide anchor missing")
io.open(p5, "w", encoding="utf-8", newline="").write(t5.replace(old5, new5, 1))
print("guide updated")
