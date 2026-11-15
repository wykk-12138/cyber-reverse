import io, json, re
segs = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))
stores = ['Nike','Popmart','PopMart','Shopify','Footlocker','Demandware','Magento','Goat','Scheels',
          'HBX','Casio','Farfetch','Warhammer','Supreme','Adidas','Yeezy','Snkrs','Amazon','Target','Walmart']
hits = []
for s in segs:
    txt = ','.join(n for _, n in s['steps'])
    found = [st for st in stores if st.lower() in txt.lower()]
    if found:
        hits.append((s['addr'], found, [n for _, n in s['steps']][:8]))
print('segments whose METHOD NAMES contain a store name:', len(hits))
for addr, found, names in hits[:10]:
    print('  %-12s %-14s %s' % (addr, ','.join(found), ', '.join(names)))
print()
# and: how many distinct method names appear in exactly one segment (distinctive by construction)?
import collections
cnt = collections.Counter(n for s in segs for _, n in s['steps'])
once = [n for n, c in cnt.items() if c == 1]
print('method names total %d, appearing in exactly one segment: %d' % (len(cnt), len(once)))
