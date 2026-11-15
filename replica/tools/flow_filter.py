import io, json, re
groups = json.load(io.open('row_groups_wide.json', encoding='utf-8'))
A = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))

FLOW = {'AddToCart','AddToCartMulti','AddToCartPreload','AddToCartStoreFront','FindProduct','FindVariant',
        'GetCheckout','GetProductHtml','SubmitOrder','SubmitShipping','SubmitBilling','GetCartCsrf',
        'SubmitEmail','SubmitDiscount','CreateCheckout','FindProductMulti','GetHome','GetCsrf',
        'GetBasket','SubmitPayment','EnterRaffle','GetLotteryForm'}
def is_flow(names):
    return len(set(names) & FLOW) >= 2

b_flows = [g for g in groups if is_flow([n for _, n in g['steps']])]
a_flows = [s for s in A if is_flow([n for _, n in s['steps']])]
print('B 布局: %d 段 -> 其中流水线 %d 段' % (len(groups), len(b_flows)))
print('A 布局: %d 段 -> 其中流水线 %d 段' % (len(A), len(a_flows)))

seen = set()
uniq = []
for g in a_flows + b_flows:
    key = tuple(sorted(n for _, n in g['steps']))
    if key in seen: continue
    seen.add(key); uniq.append(g)
print('合并去重后的流水线段:', len(uniq))
print('步数合计:', sum(len(g['steps']) for g in uniq))
print()
print('最长的 6 段:')
for g in sorted(uniq, key=lambda x: -len(x['steps']))[:6]:
    base = g.get('base') or g.get('addr')
    print('  %-12s %2d 步  %s' % (base, len(g['steps']), ', '.join(n for _, n in g['steps'][:6])))
