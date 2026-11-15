import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
lines = io.open(p, encoding='utf-8').read().splitlines()
# drop the stale declaration left from the R227 attempt (line 134, 1-based) plus its doc line above if any
idx = 133
print('removing:', repr(lines[idx]))
if lines[idx - 1].strip().startswith('///'):
    print('and its doc line:', repr(lines[idx - 1]))
    del lines[idx - 1:idx + 1]
else:
    del lines[idx]
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
print('done')
