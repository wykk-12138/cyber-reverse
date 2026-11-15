import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
# undo the two wrong hits in TaskCreatorView
t = t.replace('UiKit.Row(MonitorDelayLabel, monitor),\n            UiKit.Row(ErrorDelayLabel, retry),\n            UiKit.Row("Retry Delay", error),',
              'UiKit.Row("Monitor delay (ms)", monitor),\n            UiKit.Row("Retry delay (ms)", retry),\n            UiKit.Row("Error delay (ms)", error),', 1)
# now apply inside the group dialog only: anchor on the Timeout row that follows
old = '''        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Monitor delay (ms)", monitor),
            UiKit.Row("Retry delay (ms)", retry),
            UiKit.Row("Error delay (ms)", error),'''
new = '''        return UiKit.Scroll(UiKit.Form(
            UiKit.Row(MonitorDelayLabel, monitor),
            UiKit.Row(ErrorDelayLabel, retry),
            UiKit.Row("Retry Delay", error),'''
if old in t:
    t = t.replace(old, new, 1)
    print('group dialog rows updated')
else:
    print('group dialog anchor not found — inspecting')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
