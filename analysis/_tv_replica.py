import io, re
t = io.open(r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs", encoding='utf-8').read()
names = sorted(set(re.findall(r'public\s+(?:[\w<>,\[\]\?\.]+)\s+(\w+)\s*[\({=]', t)))
print(len(names), ':', ', '.join(names))
