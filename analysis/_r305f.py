import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs'
lines = io.open(p, encoding='utf-8').read().split('\n')
n = 0
for i, l in enumerate(lines):
    if '/v1/buys/' in l and 'inferred: no image evidence' not in l:
        lines[i] = l.rstrip() + '  // inferred: no image evidence (R294)'
        n += 1
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('marked GoatFlow /v1/buys lines:', n)
