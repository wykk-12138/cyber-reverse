import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
# lines 205/206 (1-based) are the wrong hits inside TaskCreatorView
assert 'MonitorDelayLabel' in lines[204] and 'ErrorDelayLabel' in lines[205], (lines[204], lines[205])
lines[204] = lines[204].replace('UiKit.Row(MonitorDelayLabel, monitor)', 'UiKit.Row("Monitor delay (ms)", monitor)')
lines[205] = lines[205].replace('UiKit.Row(ErrorDelayLabel, retry)', 'UiKit.Row("Retry delay (ms)", retry)')
# lines 461/462 are the group dialog's rows
assert '"Monitor delay (ms)"' in lines[460] and '"Retry delay (ms)"' in lines[461], (lines[460], lines[461])
lines[460] = lines[460].replace('UiKit.Row("Monitor delay (ms)", monitor)', 'UiKit.Row(MonitorDelayLabel, monitor)')
lines[461] = lines[461].replace('UiKit.Row("Retry delay (ms)", retry)', 'UiKit.Row(ErrorDelayLabel, retry)')
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('both sites fixed by line, after asserting each one')
