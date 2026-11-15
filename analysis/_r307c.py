import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()
for name in ('round 297 -- an unbacked cookie loses its inferred marker',
             'round 298 -- an unbacked query param loses its inferred marker'):
    i = t.index(name)
    j = t.index('"replace": "no marker here",', i)
    t = t[:j] + '"replace": "no marker here", "all": True,' + t[j+len('"replace": "no marker here",'):]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('both new mutations now replace every occurrence')
