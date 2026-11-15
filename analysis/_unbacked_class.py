import io, os
unbacked = [
 ('/account/recover','StoreFlow.cs'),('/account/verify','MagentoFlow.cs'),('/api/basket/v1/items','FarfetchFlow.cs'),
 ('/api/beast','BstnFlow.cs'),('/api/checkout/submit','RetailFlows.cs'),
 ('/api/checkout/v1/basket/{basketId}','FarfetchFlow.cs'),('/api/checkout/v1/basket/{basketId}/place-order','FarfetchFlow.cs'),
 ('/api/checkout/v1/basket/{basketId}/shipping','FarfetchFlow.cs'),('/api/order/submit','PopMartEndpoints.cs'),
 ('/api/preorder/entry','RetailFlows.cs'),('/api/search','ScheelsFlow.cs'),('/api/stock','PopMartEndpoints.cs'),
 ('/api/v2/shop/countries','HbxFlow.cs'),('/collections/new-releases','MagentoFlow.cs'),
 ('/rest/V1/carts/mine/totals','MagentoFlow.cs'),('/v1/buys','GoatFlow.cs'),
 ('/view/resources/getUserInfo','HybrisFlow.cs'),
]
base = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows'
import glob
files = {os.path.basename(f): f for f in glob.glob(os.path.join(base, '*.cs'))}
doc, code, nowhere = [], [], []
for path, fname in unbacked:
    f = files.get(fname)
    if not f:
        nowhere.append((path, fname)); continue
    lines = io.open(f, encoding='utf-8').read().split('\n')
    in_doc = any(path in l and l.lstrip().startswith('//') for l in lines)
    in_code = any(path in l and not l.lstrip().startswith('//') for l in lines)
    if in_doc: doc.append((path, fname))
    elif in_code: code.append((path, fname))
    else: nowhere.append((path, fname))
print('出现在文档注释里（= 现场抓包/观察记录）:', len(doc))
for p, f in doc: print('   %-46s %s' % (p, f))
print()
print('只出现在代码里:', len(code))
for p, f in code: print('   %-46s %s' % (p, f))
print()
print('两处都没有:', nowhere)
