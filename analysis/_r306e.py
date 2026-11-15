import io
# restore both mutated files by putting the marker text back
for p in (r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs',
          r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\FarfetchFlow.cs'):
    t = io.open(p, encoding='utf-8').read()
    n = t.count('not marked (R29')
    t = t.replace('not marked (R29', 'inferred: no image evidence (R29')
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('restored', n, 'marker(s) in', p.split('\\')[-1])
