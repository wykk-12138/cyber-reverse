import io, json, re
segs = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))

distinct = {
 'Nike':    ['Get6Js', 'GetEtJs', 'FetchSensor', 'NikeSku'],
 'Popmart': ['GetLotteryForm', 'EnterRaffle', 'CheckRaffleStatus', 'GetRaffleProduct'],
 'Shopify': ['GetCartCsrf', 'AddToCartStoreFront', 'SubmitDiscount'],
 'Demandware': ['DeleteBasket', 'SubmitBilling'],
}
print('== 只有"独有名词"才算数 ==')
found = 0
for s in segs:
    names = {n for _, n in s['steps']}
    for store, keys in distinct.items():
        hit = sorted(names & set(keys))
        if hit:
            found += 1
            print('  %-12s %2d 步 -> %-10s %s' % (s['addr'], len(s['steps']), store, ', '.join(hit)))
            print('       全段:', ', '.join('%d:%s' % (o, n) for o, n in s['steps']))
            break
print('有独有指纹的段:', found, '/', len(segs))

print()
print('== 邻居里出现商店名的段 ==')
stores = re.compile(r'(Nike|Popmart|PopMart|Shopify|Footlocker|Demandware|Magento|Goat|Scheels|HBX|Casio|Farfetch|Warhammer)')
n = 0
for s in segs:
    hit = stores.search(' '.join(s['neighbours']))
    if hit:
        n += 1
        if n <= 5:
            print('  %-12s -> %-10s 邻居: %s' % (s['addr'], hit.group(1), ' | '.join(x[:28] for x in s['neighbours'][:3])))
print('邻居含商店名的段:', n, '/', len(segs))
