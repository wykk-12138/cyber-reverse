import io, re, os, json
doc = io.open(r'replica\docs\ORIGINAL_VIEWS.md', encoding='utf-8', errors='replace').read()
rows = re.findall(r'\|\s*`Cybersole\.Ui\.Views\.([A-Za-z0-9_.]+)`\s*\|\s*`([^`]+)`', doc)
names = []
for full, path in rows:
    cls = full.split('.')[-1]
    names.append((full, cls, path))
# unique by class
seen = set(); uniq = []
for full, cls, path in names:
    if cls in seen: continue
    seen.add(cls); uniq.append((full, cls, path))
src = ''
for root, dirs, files in os.walk(r'replica\src\Cybersole.Ui'):
    if 'obj' in root or 'bin' in root: continue
    for f in files:
        if f.endswith('.cs'):
            src += io.open(os.path.join(root,f), encoding='utf-8', errors='replace').read()
missing = [u for u in uniq if ('class ' + u[1]) not in src]
print('views in doc:', len(uniq), 'present:', len(uniq)-len(missing), 'missing:', len(missing))
for full, cls, path in missing:
    print('  MISSING', full, '|', path)
