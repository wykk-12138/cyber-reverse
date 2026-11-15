import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs'
t = io.open(p, encoding='utf-8').read()

cites = {
    'popmart':            ('0x0337b9e5', '24/24 名字同序；序号差异只是粘连（1040→104、1204→120、1154→115、1354→135、1380→138、1428→142）'),
    'demandware-classic': ('0x034ac0f3', '12/12 名字同序；356/360/376 是 35/36/37 粘连'),
    'demandware-dual':    ('0x0336f0bd', '15/15 名字与序号完全一致'),
    'collectplus-app':    ('0x033929ec', '17/17 名字同序；370→37、440→44 粘连'),
}
for store, (addr, note) in cites.items():
    pat = re.compile(r'(new\("%s", new\[\]\s*\{.*?\n    \}))(\);)' % re.escape(store), re.S)
    m = pat.search(t)
    assert m, store
    t = t[:m.end(1)] + ', FlowSource.Literal' + t[m.end(1) + 2:]
print('four flows marked Literal')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
