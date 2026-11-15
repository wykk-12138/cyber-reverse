import io, json, re
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
nf = json.loads(re.match(r'\s*const GLOBAL_NOT_FN = new Set\((.*)\)\s*;?\s*$', src[160017][12:]).group(1))
print('notfn', len(nf))
print('on* in notfn:', [n for n in nf if n.startswith('on')][:20])
print('sample tail', nf[-12:])
print('oncopy in notfn:', 'oncopy' in nf, '| ongesturechange:', 'ongesturechange' in nf)
