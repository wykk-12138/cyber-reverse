import io, json, glob, os, re
flows = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\row_groups_wide.json', encoding='utf-8'))
A = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))
FLOW = {'AddToCart','AddToCartMulti','AddToCartPreload','AddToCartStoreFront','FindProduct','FindVariant',
        'GetCheckout','GetProductHtml','SubmitOrder','SubmitShipping','SubmitBilling','GetCartCsrf',
        'SubmitEmail','SubmitDiscount','CreateCheckout','FindProductMulti','GetHome','GetCsrf',
        'GetBasket','SubmitPayment','EnterRaffle','GetLotteryForm'}
pipes = [g for g in flows if len({n for _, n in g['steps']} & FLOW) >= 2]
pipes += [s for s in A if len({n for _, n in s['steps']} & FLOW) >= 2]
seen, uniq = set(), []
for g in pipes:
    k = tuple(sorted(n for _, n in g['steps']))
    if k not in seen: seen.add(k); uniq.append(g)

src = {f: io.open(f, encoding='utf-8', errors='replace').read()
       for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True)}
print('recovered pipelines:', len(uniq))
for g in uniq:
    names = [n for _, n in g['steps']]
    hits = {}
    for f, t in src.items():
        n = sum(1 for x in names if re.search(r'\b' + re.escape(x) + r'\b', t))
        if n >= 3: hits[os.path.basename(f)] = n
    best = sorted(hits.items(), key=lambda kv: -kv[1])[:2]
    base = g.get('base') or g.get('addr')
    print('  %-12s %2d 步 -> %s' % (base, len(names), best or '（复刻件里没有同名方法）'))
