import io, re, os
SRC = r"D:\projects\cyber-reverse\replica\src"
def props(cls):
    for dp, _d, fns in os.walk(SRC):
        if f"{os.sep}obj{os.sep}" in dp or f"{os.sep}bin{os.sep}" in dp: continue
        for fn in fns:
            if not fn.endswith('.cs'): continue
            t = io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
            m = re.search(r'\bclass\s+' + cls + r'\b', t)
            if not m: continue
            i = t.index('{', m.end()); depth = 0
            for j in range(i, len(t)):
                if t[j] == '{': depth += 1
                elif t[j] == '}':
                    depth -= 1
                    if depth == 0:
                        body = t[i:j]; break
            names = re.findall(r'JsonPropertyName\("([^"]+)"\)\s*\n\s*public[^;{]*?(\w+)\s*\{', body)
            out = [n for n, _ in names]
            plain = re.findall(r'public\s+[\w<>,\[\]\?\.]+\s+(\w+)\s*(?:\{\s*get|=>)', body)
            attr_props = {pname for _, pname in names}
            plain = [p for p in plain if p not in attr_props]
            return out + plain
    return None

for cls in ('AccountsDocument', 'BillingGroup', 'ProxyGroup', 'AnalyticsDocument',
            'SmartActionsDocument', 'SmartActionUtilitiesDocument', 'Profile', 'Account'):
    print('%-30s %s' % (cls, props(cls)))
