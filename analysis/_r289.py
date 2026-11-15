import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs'
t = io.open(p, encoding='utf-8').read()

notes = {
 'nike': ('0x03385576 + 0x0338562c',
          'R289: assembled from two literals of the same class — 0x03385576 carries StartEcomSession 41 … FindVariant 44, '
          '0x0338562c carries CreateBasket 46 … SubmitOrder 58. Names and order match this list exactly; the printed '
          'ordinals differ only where a digit glued (498→49, 502→50, 516→51, 526→52, 560→56).'),
 'johnlewis': ('0x0338a655 + 0x0338af47',
               'R289: 0x0338a655 carries 17 steps (GetHome 20, WebHandOver 23 … GetStripePaymentIntent 39) and the lambda '
               'row 0x0338af47 supplies the two the earlier round deduced by hand — FindProduct (g__Available|21_3) and '
               'AddToCart (b__22_0) — which is exactly where this list puts them, at 21 and 22.'),
}
for store, (addrs, note) in notes.items():
    pat = re.compile(r'new\("%s", new\[\]\s*\{.*?\n    \}\);' % re.escape(store), re.S)
    m = pat.search(t)
    assert m, store
    body = m.group(0)[:-2] + ', FlowSource.Literal);'
    t = t[:m.start()] + body + t[m.end():]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('nike and johnlewis marked Literal')
