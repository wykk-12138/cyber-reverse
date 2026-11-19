"""For each catalog literal the replica lacks, ask whether the image also carries a domain-shaped string for it.

Two outcomes matter and they mean different things:
  with-domain    - the image has something like <token>.com, so this is a store whose host is a literal and a flow
                   could be built from it
  without-domain - no such literal, which fits an id whose host arrives in the server-delivered connect/app config,
                   the same external condition that holds Farfetch's remaining steps

The probe is a positive-only search: finding a domain proves the literal exists, not finding one does not prove the
image has none, so the second bucket is reported as "no domain literal found" rather than "no domain".
"""
import io
import json
import re
import subprocess
import sys


def ida_str(pattern, limit=6):
    out = subprocess.run([sys.executable, 'analysis/ida.py', 'str', pattern, '--limit', str(limit)],
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        return json.JSONDecoder().raw_decode(out.stdout)[0]
    except Exception:
        return {'n': 0, 'matches': []}


rows = []
for line in io.open('analysis/site_catalog_classified.txt', encoding='utf-8').read().split('\n'):
    if not line or line.startswith('#'):
        continue
    parts = line.split('\t')
    if len(parts) >= 2 and parts[1].strip() == '-':
        rows.append(parts[0].strip())

print('literals absent from the replica:', len(rows))
with_domain, without_domain = [], []
for token in rows:
    low = re.sub(r'[^a-z0-9]', '', token.lower())
    if len(low) < 4:
        without_domain.append((token, '(too short to probe)'))
        continue
    hit = None
    for pattern in ('%s.com' % low, '%s.co' % low):
        d = ida_str(pattern, limit=3)
        if d.get('matches'):
            hit = d['matches'][0]['string'][:60]
            break
    if hit:
        with_domain.append((token, hit))
    else:
        without_domain.append((token, 'no domain literal found'))

print('  with a domain-shaped literal in the image: %d' % len(with_domain))
for t, h in with_domain:
    print('     %-30s %s' % (t, h))
print('  no domain literal found: %d' % len(without_domain))
for t, h in without_domain[:20]:
    print('     %-30s %s' % (t, h))
