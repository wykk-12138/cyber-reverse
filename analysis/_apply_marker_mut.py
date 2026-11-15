import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs'
t = io.open(p, encoding='utf-8').read()
io.open(r'D:\projects\cyber-reverse\analysis\_goat_backup.cs', 'w', encoding='utf-8', newline='').write(t)
mutated = t.replace('inferred: no image evidence (R294)', 'not marked', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(mutated)
print('manually mutated; marker count now', mutated.count('inferred: no image evidence (R294)'))
