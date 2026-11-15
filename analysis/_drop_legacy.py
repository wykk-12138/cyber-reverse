import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs'
lines = io.open(p, encoding='utf-8').read().splitlines()

sig = next(i for i, l in enumerate(lines) if 'private Control LegacyLeftPane()' in l)
# walk back over the doc comment block
start = sig
while start > 0 and lines[start - 1].strip().startswith('///'):
    start -= 1

depth = 0
end = None
for i in range(sig, len(lines)):
    depth += lines[i].count('{') - lines[i].count('}')
    if depth == 0 and i > sig:
        end = i
        break
assert end is not None
# also swallow one trailing blank line
tail = end + 1
while tail < len(lines) and lines[tail].strip() == '':
    tail += 1

removed = lines[start:tail]
print('removing lines', start + 1, '..', tail, '(', len(removed), 'lines )')
print('first:', removed[0].strip()[:80])
print('last :', removed[-1].strip()[:80])

out = lines[:start] + lines[tail:]
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(out) + '\n')
print('remaining lines:', len(out))
