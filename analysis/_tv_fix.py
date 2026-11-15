import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs'
t = io.open(p, encoding='utf-8').read()

# 1) drop the duplicates I added (the class already had private versions)
for name in ('StartSelected', 'StopAll', 'CloneSelected', 'DeleteSelected'):
    pat = re.compile(r'\n    /// <summary>[^\n]*</summary>\n    public void ' + name + r'\(\) => _grid\?\.\w+\(\);\n')
    t2 = pat.sub('\n', t)
    print(name, 'duplicate removed' if t2 != t else 'MISS')
    t = t2

# 2) the existing private implementations become the bound commands
for name in ('StartSelected', 'StopAll', 'CloneSelected', 'DeleteSelected', 'DeleteTasks'):
    old = f'    private void {name}('
    if old in t:
        t = t.replace(old, f'    public void {name}(', 1)
        print('flipped', name)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
