import io, json, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def text_at(lineno):
    ln = src[lineno-1]
    return ln[12:]          # "0x%08x" + two spaces
lines = [(n, text_at(n)) for n in range(158471, 158483)]
for n, t in lines:
    print(n, len(t), repr(t[:70]))
rules = [t for n, t in lines if t.strip().startswith('{ match:')]
print('rule lines', len(rules))
joined = '\n'.join([lines[0][1]] + [t.rstrip() for n, t in lines[1:] if True])
print('joined head', repr(joined[:80]))
print('joined tail', repr(joined[-80:]))
# count names per rule crudely
for t in rules:
    m = re.search(r"names: \[(.*?)\]", t)
    print('  bytes', len(t), 'names', 0 if not m or not m.group(1).strip() else m.group(1).count('",')+1)
io.open('_order_rules.txt','w',encoding='utf-8',newline='').write(joined)
