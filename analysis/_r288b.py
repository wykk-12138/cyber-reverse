import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs'
t = io.open(p, encoding='utf-8').read()
for store in ('popmart', 'demandware-classic', 'demandware-dual', 'collectplus-app'):
    pat = re.compile(r'new\("%s", new\[\]\s*\{.*?\n    \}\);' % re.escape(store), re.S)
    m = pat.search(t)
    assert m, store
    body = m.group(0)
    assert body.endswith(');'), body[-20:]
    new_body = body[:-2] + ', FlowSource.Literal);'
    t = t[:m.start()] + new_body + t[m.end():]
print('four flows marked Literal')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
