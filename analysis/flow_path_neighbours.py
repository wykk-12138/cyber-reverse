"""For each unanswered flow path, look for a near neighbour in the full string dump.

The audit says which literals have no exact hit; it does not say why. This narrows the why by searching the same
complete dump for the literal's last two path segments, so a row either points at a variant the image really uses
(different spelling, same intent) or reports that nothing in the image resembles it at all.
"""
import io
import re
import sys

DUMP = 'analysis/ida_strings.txt'
AUDIT = 'analysis/flow_path_audit.txt'
OUT = 'analysis/flow_path_neighbours.txt'


def load(path):
    text = io.open(path, encoding='utf-8', errors='replace').read()
    return text.replace('\\n', '\n').split('\n')


def main():
    rows = [l for l in io.open(DUMP, encoding='utf-8', errors='replace')
            if '\t' in l]
    strings = [l.split('\t', 1)[1].rstrip('\n') for l in rows]

    targets = []
    in_no_hit = False
    for line in io.open(AUDIT, encoding='utf-8', errors='replace'):
        if line.startswith('# NO-HIT'):
            in_no_hit = True
            continue
        if in_no_hit and line.startswith('# ') and '(' in line:
            # R1249: the audit writes no-hit first and then prefix-only/exact/prose, so the first version swallowed
            # 265 rows instead of 26. The next section header ends this one.
            break
        if in_no_hit and line and not line.startswith('#'):
            parts = line.rstrip('\n').split('\t')
            # R1252: the audit pads its first column with %-58s, and the previous version read that column raw, so
            # every key carried trailing spaces and nothing could ever match -- which is exactly how R1249 concluded
            # "zero neighbours" for all twenty-six. The stripped column is the fix; the conclusion has to be redone.
            lit = parts[0].strip()
            if lit:
                targets.append((lit, parts[-1].strip()))

    print('no-hit literals to explain: %d' % len(targets))
    out = []
    for lit, src in targets:
        segs = [s for s in lit.split('?')[0].split('/') if s and not s.startswith('{')]
        key = '/'.join(segs[-2:]) if len(segs) >= 2 else (segs[-1] if segs else lit)
        hits = [s for s in strings if key and key.lower() in s.lower()][:3]
        out.append((lit, src, key, hits))

    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Near neighbours for every no-hit flow path, searched in analysis/ida_strings.txt (full list).\n')
        f.write('# key = the literal\'s last two path segments. A hit means the image holds something similar, so the\n')
        f.write('# row is a spelling/variant question; no hit means nothing in the image resembles it, which is the\n')
        f.write('# only shape that can indicate the replica invented a route.\n')
        f.write('# Regenerate with: python analysis/flow_path_neighbours.py\n\n')
        for lit, src, key, hits in out:
            f.write('%-46s\t%-22s\tkey=%-28s\t%s\n'
                    % (lit, src, key, '; '.join(h[:60] for h in hits) if hits else 'NO NEIGHBOUR'))
    print('with a neighbour : %d' % sum(1 for _l, _s, _k, h in out if h))
    print('no neighbour     : %d' % sum(1 for _l, _s, _k, h in out if not h))
    print('\nno neighbour rows:')
    for lit, src, key, hits in out:
        if not hits:
            print('   %-44s %-20s key=%s' % (lit[:44], src, key))
    print('\nwrote', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
