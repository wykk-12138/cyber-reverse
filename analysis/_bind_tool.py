import io
p = r'D:\projects\cyber-reverse\replica\tools\bind_diff.py'
t = io.open(p, encoding='utf-8').read()
# teach the tool to bucket the gap the way the doc does, so the two can be compared at a glance
t = t.replace('''for typ, n, miss, missing in sorted([r for r in rows if r[2]], key=lambda r: -r[2])[:20]:''',
'''NOISE = re.compile(r'^HasMultiple_\\d+$')      # generic instantiation artefacts, not design members
if '--buckets' in sys.argv:
    noise = sum(1 for r in rows if r[2] for m in r[3] if NOISE.match(m))
    real = missing_total - noise
    print(f'noise (HasMultiple_NN): {noise}')
    print(f'real gap              : {real}')
    print()
    for typ, n, miss, missing in sorted([r for r in rows if r[2]], key=lambda r: -r[2]):
        real_missing = [m for m in missing if not NOISE.match(m)]
        if real_missing:
            print('  %-50s %2d  %s' % (typ.split('Cybersole.')[-1], len(real_missing), ', '.join(real_missing[:8])))
    sys.exit(0)

for typ, n, miss, missing in sorted([r for r in rows if r[2]], key=lambda r: -r[2])[:20]:''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('bind_diff.py learned --buckets')
