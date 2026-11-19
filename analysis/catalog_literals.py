import glob
import io
import json
import subprocess
import sys

CODE = r'''
import idautils, idc, ida_funcs, json
f = ida_funcs.get_func(0x140F7DDE0)
res = []
ea = f.start_ea
while ea < f.end_ea:
    if idc.print_insn_mnem(ea) in ('lea', 'mov'):
        for x in idautils.XrefsFrom(ea):
            if x.to >= 0x143000000:
                res.append(x.to)
    nxt = idc.next_head(ea, f.end_ea)
    if nxt <= ea:
        break
    ea = nxt
print(json.dumps(sorted(set(res))))
'''

out = subprocess.run([sys.executable, 'analysis/ida.py', 'py', CODE, '--timeout', '900'],
                     capture_output=True, text=True, encoding='utf-8', errors='replace')
doc = json.JSONDecoder().raw_decode(out.stdout)[0]
addrs = json.loads((doc.get('stdout') or '').strip().split('\n')[-1])
print('referenced addresses:', len(addrs))

names = subprocess.run([sys.executable, 'analysis/names_at.py'] + [hex(a) for a in addrs],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')

entries = []
for line in (names.stdout or '').split('\n'):
    s = line.strip()
    if not (s.startswith('0x') and ' str ' in s):
        continue
    addr, rest = s.split(' ', 1)
    m = rest.rsplit("'", 2)
    if len(m) >= 2:
        entries.append((addr, m[-2]))

print('decoded strings:', len(entries))
with io.open('analysis/site_catalog_names.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write('# Literals referenced by sub_140F7DDE0 (70,719 bytes), the settings-descriptor/catalog builder.\n')
    f.write('# Reached by walking the function and collecting every lea/mov xref target at or above 0x143000000.\n')
    f.write('# Regenerate with the scan recorded in R1230; this file is a straight dump, not a filtered list.\n')
    f.write('# count=%d\n\n' % len(entries))
    for addr, text in entries:
        f.write('%s\t%s\n' % (addr, text))

replica = '\n'.join(io.open(p, encoding='utf-8', errors='replace').read()
                    for p in glob.glob('replica/src/**/*.cs', recursive=True))
present = [t for _a, t in entries if t and t in replica]
print('of those, the same literal appears in replica/src: %d' % len(present))
print('sample present:', ', '.join(present[:12]))
print('wrote analysis/site_catalog_names.txt')
