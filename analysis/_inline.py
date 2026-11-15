import io
pool = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read()
cases = [
 ("FarfetchFlow:161","/api/basket/v1/items","basket/v1/items"),
 ("GoatFlow:193","/v1/buys","v1/buys"),
 ("HbxFlow:41","/api/v2/shop/countries","shop/countries"),
 ("HybrisFlow:60","/view/resources/getUserInfo","getUserInfo"),
 ("Magento:180","/rest/V2/carts/mine","carts/mine"),
 ("Magento:223","/rest/V1/carts/mine/totals","carts/mine/totals"),
 ("Magento:559","/account/verify","account/verify"),
 ("Magento:833","/collections/new-releases","new-releases"),
 ("Retail:39","https://yzy-prod.swell.store","yzy"),
 ("Retail:747","/v1/public/raffle-entry","raffle"),
 ("Retail:965","/api/checkout/submit","checkout/submit"),
 ("Retail:1115","/api/preorder/entry","preorder"),
 ("Scheels:33","https://search.scheels.com","search.scheels.com"),
 ("Scheels:206","/api/search","/api/search"),
 ("Scheels:230","/api/cart/items","cart/items"),
 ("Store:686","/checkout/complete","checkout/complete"),
 ("Store:893","https://api.paypal.com/v1/oauth2/token","oauth2/token"),
 ("Store:1013","https://p01.mul-pay.jp/payment/SaveCard.idPass","SaveCard"),
 ("Store:1160","/account/recover","account/recover"),
 ("Store:1516","https://a.klaviyo.com/client/subscriptions/confirm","klaviyo"),
 ("Store:1613","/buy/carts/v2/app","carts/v2/app"),
 ("Store:1671","/account?email=","account?email"),
]
for name, lit, frag in cases:
    hit = lit in pool
    frag_hit = pool.find(frag)
    print(f'{name:22s} verbatim={hit!s:5s} frag={frag!r:28s} frag_in_pool={"yes" if frag_hit>=0 else "NO"}')
