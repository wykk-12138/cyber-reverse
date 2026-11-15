import io, json
segs = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))
segs.sort(key=lambda s: int(s['addr'], 16))
jl = [s for s in segs if any(n in ('GetProductHtml','AddToCartPreload','GetPayPalOrderId') for _, n in s['steps'])]
print('John Lewis candidates:', len(jl))
for s in jl:
    print(' ', s['addr'], '->', ', '.join('%d:%s' % (o, n) for o, n in s['steps']))
print()
print('all 69 segment addresses (sorted):')
print('  ' + ' '.join(s['addr'] for s in segs))
