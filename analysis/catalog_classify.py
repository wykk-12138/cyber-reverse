"""Classify the literals sub_140F7DDE0 references, and check the id halves against the replica's store catalog.

The distinction that matters is display name versus id: the builder emits {name, display, typeId, flag}, so a store
contributes two literals and only one of them is an identifier. Reporting all eighty-eight as stores would overstate
the roster by roughly a factor of two, which is the same mistake the prefix buckets made in R1223.

Classification is rule-based and named as such:
  pair      - a spaced display name with an unspaced twin in the same set (Dicks Sporting Goods / DicksSportingGoods)
  test      - the literal says Test
  utility   - no letters-after-space pattern and it looks like a token, number pattern or log string
  unpaired  - a single-token name with no twin, which is what most one-word stores look like
"""
import glob
import io
import re

rows = []
for line in io.open('analysis/site_catalog_names.txt', encoding='utf-8').read().split('\n'):
    if not line or line.startswith('#'):
        continue
    parts = line.split('\t')
    if len(parts) >= 2:
        rows.append((parts[0], parts[1]))

texts = [t for _a, t in rows]
lower = {t.lower(): t for t in texts}

pairs = {}
for t in texts:
    if ' ' in t:
        joined = t.replace(' ', '')
        if joined.lower() in lower:
            pairs[t] = lower[joined.lower()]
            pairs[lower[joined.lower()]] = t

# R1231: the first version tested `t in replica`, which is case sensitive, so NikeGS looked absent while the
# replica spells it NikeGsFlow. Identifiers differ in case between the image and the replica, so this compares
# case-insensitively; the earlier reading was a false positive in my own script, not a gap.
replica = '\n'.join(io.open(p, encoding='utf-8', errors='replace').read()
                    for p in glob.glob('replica/src/**/*.cs', recursive=True)).lower()


def in_replica(text):
    return text.lower() in replica

buckets = {'pair-display': [], 'pair-id': [], 'test': [], 'utility': [], 'unpaired': []}
for t in texts:
    if t in pairs:
        buckets['pair-display' if ' ' in t else 'pair-id'].append(t)
    elif 'test' in t.lower():
        buckets['test'].append(t)
    elif re.search(r'[\\^$\[\]]|^\d|\.', t) or t in ('Buffering', 'AO'):
        buckets['utility'].append(t)
    else:
        buckets['unpaired'].append(t)

out = 'analysis/site_catalog_classified.txt'
with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('# Classification of the %d literals referenced by sub_140F7DDE0.\n' % len(texts))
    f.write('# pair-display / pair-id are the two halves of one catalog entry (display name and id).\n')
    f.write('# "in replica" means the same literal appears somewhere under replica/src; it does not\n')
    f.write('# prove the replica lists that store in its catalog, only that the token exists there.\n')
    f.write('# Regenerate with: python analysis/catalog_classify.py\n\n')
    for name in ('pair-id', 'pair-display', 'unpaired', 'test', 'utility'):
        items = sorted(buckets[name])
        hit = [t for t in items if in_replica(t)]
        f.write('# %s: %d total, %d appear in replica/src\n' % (name, len(items), len(hit)))
        for t in items:
            f.write('%-30s\t%s\n' % (t, 'in-replica' if in_replica(t) else '-'))
        f.write('\n')

print('literals: %d' % len(texts))
for name in ('pair-id', 'pair-display', 'unpaired', 'test', 'utility'):
    items = buckets[name]
    hit = sum(1 for t in items if in_replica(t))
    print('  %-12s %3d  (in replica: %d)' % (name, len(items), hit))
print('\nid halves the replica does not contain:')
missing = [t for t in sorted(buckets['pair-id']) if not in_replica(t)]
print('  ' + (', '.join(missing) if missing else '(none)'))
print('wrote', out)
