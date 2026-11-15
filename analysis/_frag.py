import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
frags = ['carts/mine','new-releases','yzy','raffle','preorder','cart/items','oauth2','SaveCard','klaviyo','pocketgames','swell']
for f in frags:
    print('====', f)
    n = 0
    for ln in lines:
        m = pat.match(ln)
        if not m: continue
        if f in m.group(2):
            print('  ', m.group(1), m.group(2)[:130])
            n += 1
            if n >= 4: break
    if n == 0: print('   (none)')
