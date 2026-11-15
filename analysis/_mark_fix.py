import io, os
MARK = '  // inferred: no image evidence (R294)'
targets = [
 ('/account/recover','src/Cybersole.Stores/Flows/StoreFlow.cs'),
 ('/account/verify','src/Cybersole.Stores/Flows/MagentoFlow.cs'),
 ('/api/basket/v1/items','src/Cybersole.Stores/Flows/FarfetchFlow.cs'),
 ('/api/beast','src/Cybersole.Stores/Flows/BstnFlow.cs'),
 ('/api/checkout/submit','src/Cybersole.Stores/Flows/RetailFlows.cs'),
 ('/api/checkout/v1/basket/{basketId}','src/Cybersole.Stores/Flows/FarfetchFlow.cs'),
 ('/api/checkout/v1/basket/{basketId}/place-order','src/Cybersole.Stores/Flows/FarfetchFlow.cs'),
 ('/api/checkout/v1/basket/{basketId}/shipping','src/Cybersole.Stores/Flows/FarfetchFlow.cs'),
 ('/api/order/submit','src/Cybersole.Stores/Flows/PopMartEndpoints.cs'),
 ('/api/preorder/entry','src/Cybersole.Stores/Flows/RetailFlows.cs'),
 ('/api/search','src/Cybersole.Stores/Flows/ScheelsFlow.cs'),
 ('/api/stock','src/Cybersole.Stores/Flows/PopMartEndpoints.cs'),
 ('/api/v2/shop/countries','src/Cybersole.Stores/Flows/HbxFlow.cs'),
 ('/collections/new-releases','src/Cybersole.Stores/Flows/MagentoFlow.cs'),
 ('/rest/V1/carts/mine/totals','src/Cybersole.Stores/Flows/MagentoFlow.cs'),
 ('/v1/buys','src/Cybersole.Stores/Flows/GoatFlow.cs'),
 ('/view/resources/getUserInfo','src/Cybersole.Stores/Flows/HybrisFlow.cs'),
]
report = []
for path, rel in targets:
    full = os.path.join(r'D:\projects\cyber-reverse\replica', rel.replace('/', os.sep))
    lines = io.open(full, encoding='utf-8').read().split('\n')
    # remove markers from comment-only lines for this path
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if path in line and stripped.startswith('//') and MARK in line:
            lines[i] = line.replace(MARK, '').rstrip()
    # prefer a code line
    placed = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if path in line and not stripped.startswith('//') and MARK not in line:
            lines[i] = line.rstrip() + MARK
            placed = True
            break
    if not placed:
        for i, line in enumerate(lines):
            if path in line and MARK not in line:
                lines[i] = line.rstrip() + MARK
                placed = True
                break
    io.open(full, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    report.append((path, rel, placed))
print('re-placed:', sum(1 for _, _, p in report if p), '/', len(report))
