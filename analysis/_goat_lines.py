import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs'
lines = io.open(p, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines, 1):
    if '/v1/buys' in l:
        print('%4d  marker=%s  %s' % (i, 'inferred: no image evidence' in l, l.strip()[:110]))
