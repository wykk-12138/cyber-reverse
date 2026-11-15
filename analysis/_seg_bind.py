import io, json, re
segs = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))

fps = {
 'Nike':       ['Get6Js', 'GetEtJs', 'FetchSensor', 'NikeSku', 'GetNikeSku'],
 'Popmart':    ['GetLotteryForm', 'EnterRaffle', 'CheckRaffleStatus', 'GetRaffleProduct'],
 'Shopify':    ['GetCartCsrf', 'AddToCartStoreFront', 'CreateCheckout', 'SubmitDiscount', 'GetCheckoutHtml'],
 'Footlocker': ['SubmitOrder', 'GetCsrf', 'SubmitRate', 'SubmitShipping'],
 'Demandware': ['GetBasket', 'DeleteBasket', 'SubmitBilling', 'GetShippingRates'],
 'Magento':    ['CreateCart', 'AddToCartMulti', 'GetCartItemId'],
 'Goat':       ['CreateCustomCheckout', 'GetVerificationToken'],
 'Scheels':    ['GetProductDetails', 'StartPayPalExpress'],
}

scored = []
for s in segs:
    names = {n for _, n in s['steps']}
    row = {}
    for store, keys in fps.items():
        hit = names & set(keys)
        if hit: row[store] = sorted(hit)
    if row:
        scored.append((s['addr'], len(s['steps']), row))

print('segments with a store fingerprint: %d / %d' % (len(scored), len(segs)))
for addr, n, row in sorted(scored, key=lambda r: -max(len(v) for v in r[2].values()))[:12]:
    best = max(row.items(), key=lambda kv: len(kv[1]))
    print('  %-12s %2d 步  -> %-11s %s' % (addr, n, best[0], ', '.join(best[1])))
