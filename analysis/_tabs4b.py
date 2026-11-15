import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
# BuildGeneral: lines 356..373 (1-based) -> indices 355..372
# BuildManual: line 503 to end of class (before the next '}' of class)
def find(name):
    return next(i for i, l in enumerate(lines) if name in l)

g = find('private Control BuildGeneral()')
d = find('private Control BuildDelays()')
m = find('private Control BuildManual()')
# everything after BuildManual belongs to it until the class closes; find the class-closing line
print('general', g + 1, 'delays', d + 1, 'manual', m + 1, 'last lines:', [l.strip() for l in lines[-3:]])
# remove manual first (later in the file) then general, to keep indices valid
tail = lines[m:]
# find the end: the class closing brace -- BuildManual is the last method, so drop to the last '}' of the class
end = len(lines) - 1
while lines[end].strip() == '':
    end -= 1
print('class close at', end + 1, repr(lines[end]))
lines = lines[:m] + lines[end:]
g = next(i for i, l in enumerate(lines) if 'private Control BuildGeneral()' in l)
d = next(i for i, l in enumerate(lines) if 'private Control BuildDelays()' in l)
lines = lines[:g] + lines[d:]
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('BuildGeneral and BuildManual removed')
