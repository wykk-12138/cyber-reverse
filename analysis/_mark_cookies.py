import io, os
MARK = '  // inferred: no image evidence (R297)'
edits = [
 ('src/Cybersole.Stores/Flows/NikeFlow.cs', 'c.Session.Cookies.TryGetValue("NIKE_COMMERCE_COUNTRY"'),
 ('src/Cybersole.Stores/Flows/FarfetchFlow.cs', '<c>ffid</c>'),
 ('src/Cybersole.Stores/Flows/StoreFlow.cs', 'Cookies.TryGetValue("sbsd"'),
]
for rel, needle in edits:
    full = os.path.join(r'D:\projects\cyber-reverse\replica', rel.replace('/', os.sep))
    lines = io.open(full, encoding='utf-8').read().split('\n')
    done = False
    for i, line in enumerate(lines):
        if needle in line and MARK not in line:
            lines[i] = line.rstrip() + (MARK if not line.lstrip().startswith('//') else '  // inferred: no image evidence (R297)')
            done = True
            break
    io.open(full, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print(('marked ' if done else 'MISS   ') + rel + ' :: ' + needle)
