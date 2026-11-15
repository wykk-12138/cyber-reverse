import io, re, os
doc = io.open(r'replica\docs\ORIGINAL_VIEWS.md', encoding='utf-8', errors='replace').read()
found = re.findall(r'Cybersole\.Ui\.Views\.([A-Za-z0-9_.]+)', doc)
uniq = []
seen = set()
for full in found:
    cls = full.split('.')[-1]
    if cls in seen: continue
    seen.add(cls); uniq.append((full, cls))
src = ''
for root, dirs, files in os.walk(r'replica\src\Cybersole.Ui'):
    if 'obj' in root or 'bin' in root: continue
    for f in files:
        if f.endswith('.cs'):
            src += io.open(os.path.join(root,f), encoding='utf-8', errors='replace').read()
missing = [u for u in uniq if ('class ' + u[1]) not in src]
print('unique view classes in doc:', len(uniq))
print('present:', len(uniq)-len(missing), ' missing:', len(missing))
for full, cls in missing: print('  MISSING', full)
