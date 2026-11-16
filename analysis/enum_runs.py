import idautils, json, re

MARK = chr(62) + 'd__'
PAT = re.compile('<' + '([A-Za-z_][A-Za-z0-9_]*)' + MARK + '([0-9]+)')
runs = []
total = 0
for s in idautils.Strings():
    t = str(s)
    if MARK not in t:
        continue
    total += 1
    found = [(n, int(o)) for n, o in PAT.findall(t)]
    if len(found) < 4:
        continue
    cur = [found[0]]
    for prev, nxt in zip(found, found[1:]):
        gap = nxt[1] - prev[1]
        if 0 < gap <= 3:
            cur.append(nxt)
        else:
            if len(cur) >= 4:
                runs.append((hex(s.ea), cur))
            cur = [nxt]
    if len(cur) >= 4:
        runs.append((hex(s.ea), cur))

out = {'d__strings': total, 'runs': len(runs),
       'detail': [[a, [n for n, _ in st]] for a, st in runs]}
print(json.dumps(out))
