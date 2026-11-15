import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
i = next(k for k, l in enumerate(lines) if l.strip() == 'UiKit.Caption("Add webhooks under Settings' or 'Add webhooks under Settings' in l)
j = next(k for k in range(i, len(lines)) if lines[k].strip() == '}')
print('notifications ends at', j + 1)
# the class brace is missing right after j
if lines[j + 1].strip() != '' or True:
    lines.insert(j + 1, '')
    lines.insert(j + 2, '}')
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('class closing brace restored')
