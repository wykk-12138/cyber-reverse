import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs'
t = io.open(p, encoding='utf-8').read()
find = 'inferred: no image evidence (R294)'
print('occurrences:', t.count(find))
i = t.index(find)
line = t[:i].count('\n') + 1
print('first occurrence at line', line)
print('line text:', t.split('\n')[line-1].strip()[:120])
