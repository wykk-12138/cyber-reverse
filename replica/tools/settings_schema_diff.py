import io, json, os, re

live_path = os.path.expandvars(r"%APPDATA%\Cybersole\settings.json")
live = json.loads(io.open(live_path, encoding='utf-8-sig', errors='replace').read())

src = io.open(r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs", encoding='utf-8').read()
start = src.index('class GlobalSettings')
# brace-matched body
depth = 0
for i in range(src.index('{', start), len(src)):
    if src[i] == '{': depth += 1
    elif src[i] == '}':
        depth -= 1
        if depth == 0:
            body = src[src.index('{', start):i+1]
            break

props = sorted(set(re.findall(r'public\s+[\w<>,\[\]\?\.]+\s+(\w+)\s*\{\s*get', body)))
def camel(p): return p[0].lower() + p[1:]

live_keys = [k for k in live.keys()]
prop_keys = [camel(p) for p in props]

missing = [k for k in live_keys if k not in prop_keys]
extra = [k for k in prop_keys if k not in live_keys]

print('live top-level keys :', len(live_keys))
print('replica properties  :', len(prop_keys))
print()
print('in the live file but NOT in the replica:', len(missing))
for k in missing: print('   +', k, '(' + type(live[k]).__name__ + ')')
print()
print('in the replica but NOT in the live file:', len(extra))
for k in extra: print('   -', k)
