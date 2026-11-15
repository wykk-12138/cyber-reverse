import io, re, os
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t = io.open(p, encoding='utf-8').read()
m = re.search(r'class TaskGroup\b', t)
i = t.index('{', m.end()); depth = 0
for j in range(i, len(t)):
    if t[j] == '{': depth += 1
    elif t[j] == '}':
        depth -= 1
        if depth == 0:
            body = t[i:j]; break
props = re.findall(r'public\s+[\w<>,\[\]\?\.]+\s+(\w+)\s*(?:\{\s*get|=>)', body)
print('TaskGroup properties (%d):' % len(props))
print(', '.join(props))
