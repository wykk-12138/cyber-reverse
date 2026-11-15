import io, os
# prove the two strengthened guards are not decorative: remove one marker, run, restore
cases = [
 (r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs', 'productTemplateId', 'QueryParamEvidenceRatchetTests'),
 (r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\FarfetchFlow.cs', 'ffid', 'CookieEvidenceRatchetTests'),
]
for p, needle, cls in cases:
    orig = io.open(p, encoding='utf-8').read()
    lines = orig.split('\n')
    done = False
    for i, l in enumerate(lines):
        if needle in l and 'inferred: no image evidence' in l and not l.strip().startswith('//'):
            lines[i] = l.replace('inferred: no image evidence (R29', 'not marked (R29')
            done = True
            break
    io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print(('mutated ' if done else 'COULD NOT MUTATE ') + needle)
io.open(r'D:\projects\cyber-reverse\analysis\_mut_restore.json', 'w', encoding='utf-8').write('{}')
