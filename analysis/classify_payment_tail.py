"""R1381 (fixed R1382): classify the genuinely ABSENT payment-family async names from async_tail.py.

R1382 denominator fix: the R1381 version stated it was testing the 64 absent payment names from
docs/ASYNC_TAIL.md, but actually scanned ida_strings.txt for ALL 243 payment-keyword state machines
(of which ~80 already appeared in replica/src) and then summed 237 + 30 = 267. This now imports
async_tail.py's exact classification so it tests ONLY the genuinely absent payment names.

Usage: python analysis/classify_payment_tail.py
"""
import io
import json
import sys

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'analysis')

from async_tail import classify, family_of, image_names, replica_sources  # noqa: E402
from pe_read_direct import Image  # noqa: E402

DUMP = 'analysis/ida_strings.txt'
IMAGE = 'target/Cybersole.exe'


def absent_payment_names():
    counts = {n: c for n, c in image_names().items() if family_of(n) == 'payment'}
    source = replica_sources()
    _declared, _mentioned, absent = classify(counts, source)
    return sorted(absent)


def exact_strings():
    found = {}
    for line in io.open(DUMP, encoding='utf-8', errors='replace'):
        parts = line.rstrip('\n').split('\t', 1)
        if len(parts) != 2:
            continue
        text = parts[1].strip()
        if 4 <= len(text) <= 80 and text not in found:
            found[text] = int(parts[0], 16)
    return found


def find_disp32_fast(text_bytes, text_va, targets):
    """Vectorized disp32 lookup across all 4 byte alignments of .text."""
    hits = {t: [] for t in targets}
    if not targets:
        return hits
    t_arr = np.array(sorted(targets), dtype=np.int64)
    for align in range(4):
        arr = np.frombuffer(text_bytes, dtype='<i4', offset=align, count=(len(text_bytes) - align) // 4)
        vas = text_va + align + np.arange(len(arr), dtype=np.int64) * 4
        dests = vas + 4 + arr.astype(np.int64)
        mask = np.isin(dests, t_arr)
        for idx in np.nonzero(mask)[0]:
            hits[int(dests[idx])].append(int(vas[idx]))
    for t in hits:
        hits[t].sort()
    return hits


def main():
    image = Image(IMAGE)
    names = absent_payment_names()
    pool = exact_strings()

    sec = [s for s in image.sections if s['name'] == '.text'][0]
    text_bytes = image.data[sec['raw']:sec['raw'] + min(sec['vsize'], sec['raw_size'])]
    text_va = image.image_base + sec['va']

    targets = set()
    for name in names:
        addr = pool.get(name)
        if addr is not None:
            targets.add(addr - 12)
            targets.add(addr)
    ref_map = find_disp32_fast(text_bytes, text_va, targets)

    followable, metadata_only = [], []
    for name in names:
        address = pool.get(name)
        if address is None:
            metadata_only.append((name, 'no standalone string'))
            continue

        hits = ref_map.get(address - 12, []) + ref_map.get(address, [])
        if hits:
            followable.append((name, address, hits[0]))
        else:
            metadata_only.append((name, 'standalone string, no reference'))

    print('absent payment-family async names (from async_tail): %d' % len(names))
    print('  followable to a handler: %d' % len(followable))
    print('  metadata only:           %d' % len(metadata_only))
    print()

    for name, address, site in followable:
        fn = image.function_start(site)
        print('  %-44s str %#x  first site %#x  func %s' % (
            name, address, site, ('%#x' % fn) if fn else '?'))

    print()
    print('metadata-only names (first 20):')
    for name, reason in metadata_only[:20]:
        print('  %-44s %s' % (name, reason))

    record = {
        'basis': 'async_tail absent payment family (R1382 fixed denominator)',
        'names': len(names),
        'followable': [{'name': n, 'address': hex(a), 'site': hex(s),
                        'function': hex(image.function_start(s)) if image.function_start(s) else None}
                       for n, a, s in followable],
        'metadata_only': [{'name': n, 'reason': r} for n, r in metadata_only],
    }
    io.open('analysis/.payment_tail.json', 'w', encoding='utf-8', newline='').write(
        json.dumps(record, ensure_ascii=False, indent=1))
    print()
    print('wrote analysis/.payment_tail.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
