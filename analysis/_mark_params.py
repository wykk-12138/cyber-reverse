import io, os
MARK = '  // inferred: no image evidence (R298)'
targets = [
 ('src/Cybersole.Services/Captcha/ThirdPartyDrivers.cs', 'json='),
 ('src/Cybersole.Stores/Flows/DemandwareFlow.cs', 'orderID='),
 ('src/Cybersole.Stores/Flows/DemandwareFlow.cs', 'siteId='),
 ('src/Cybersole.Stores/Flows/GoatFlow.cs', 'productTemplateId'),
]
for rel, needle in targets:
    full = os.path.join(r'D:\projects\cyber-reverse\replica', rel.replace('/', os.sep))
    lines = io.open(full, encoding='utf-8').read().split('\n')
    done = False
    for i, line in enumerate(lines):
        if needle in line and 'R298' not in line:
            lines[i] = line.rstrip() + (MARK if not line.lstrip().startswith('//') else '  // inferred: no image evidence (R298)')
            done = True
            break
    io.open(full, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print(('marked ' if done else 'MISS   ') + rel + ' :: ' + needle)
