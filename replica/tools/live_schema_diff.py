import io, json, os, re

APPDATA = os.path.expandvars(r"%APPDATA%\Cybersole")
SRC = r"D:\projects\cyber-reverse\replica\src"

# live file -> (class name, path into the json to reach the object, or None for top-level dict)
TARGETS = [
    ("settings.json", "GlobalSettings", None),
    ("tasks.json", "TaskGroup", "[]"),
    ("solvers.json", None, None),
    ("billing.json", None, None),
    ("accounts.json", None, None),
    ("proxies.json", None, None),
    ("smartActions.json", None, None),
]

def class_props(name):
    for dirpath, _d, fns in os.walk(SRC):
        if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
            continue
        for fn in fns:
            if not fn.endswith('.cs'):
                continue
            t = io.open(os.path.join(dirpath, fn), encoding='utf-8', errors='replace').read()
            m = re.search(r'\bclass\s+' + name + r'\b', t)
            if not m:
                continue
            i = t.index('{', m.end())
            depth = 0
            for j in range(i, len(t)):
                if t[j] == '{': depth += 1
                elif t[j] == '}':
                    depth -= 1
                    if depth == 0:
                        body = t[i:j]
                        break
            # both property shapes: accessor blocks and expression-bodied ("public int Running => …");
            # the first version of this tool only matched the former and reported a present member as missing.
            props = sorted(set(re.findall(r'public\s+[\w<>,\[\]\?\.]+\s+(\w+)\s*(?:\{\s*get|=>)', body)))
            return props
    return None

for fn, cls, path in TARGETS:
    p = os.path.join(APPDATA, fn)
    if not os.path.exists(p):
        continue
    raw = io.open(p, encoding='utf-8-sig', errors='replace').read()
    if not raw.strip():
        print(fn, '-> empty file')
        continue
    try:
        d = json.loads(raw)
    except Exception as e:
        print(fn, '-> parse error', e)
        continue

    if cls is None:
        if isinstance(d, list) and d and isinstance(d[0], dict):
            print('%-20s list[%d], first keys: %s' % (fn, len(d), ', '.join(list(d[0].keys())[:12])))
        elif isinstance(d, dict):
            print('%-20s dict keys: %s' % (fn, ', '.join(list(d.keys())[:12])))
        else:
            print('%-20s %s' % (fn, type(d).__name__))
        continue

    obj = d[0] if path == '[]' and isinstance(d, list) and d else d
    props = class_props(cls) or []
    camel = {p[0].lower() + p[1:]: p for p in props}
    live = [k for k in obj.keys()]
    missing = [k for k in live if k not in camel]
    print('%-20s %-16s live=%d replica=%d  missing-in-replica=%s'
          % (fn, cls, len(live), len(props), missing if missing else 'none'))
