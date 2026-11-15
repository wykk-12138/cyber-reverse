import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('UiKit.Button("Delete", DeleteGroup, danger: true),', 'UiKit.Button("Delete", DeleteGroup),')
# remove the stale name wiring the earlier surgery left behind
lines = t.split('\n')
out = [l for l in lines if 'name.TextChanged' not in l or 'groupName' in l]
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(out))
print('danger arg + stale line removed')
