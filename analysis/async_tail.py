"""Which async state-machine methods the image names but the replica has no method for.

WHY THIS EXISTS: the census quotes "124 payment async names (195 occurrences)" and the roadmap quotes
"77 still uncovered", but neither comes with the list of names -- so a session that wants to work the
tail has to take the count on faith. This derives the list from two things that can be recomputed:
the image's own `<Name>d__NN` state-machine strings (NativeAOT keeps them, which is why they show up in
the string database) and a search of replica/src for a method of that name.

Three honest limits, all of which the output states:
  - a name present in the image may belong to a namespace this replica models under a different name,
    so "missing" here means "no method of that exact name", not "no behaviour";
  - the pool is every async method in the image, not just payments, so the family column is a keyword
    guess and the caller should filter rather than trust the grouping;
  - a method can exist under `<Name>` inside a generated wrapper and still not match, because the
    search looks for a declaration of that exact identifier.

Usage:
    python analysis/async_tail.py                 # summary + the missing names
    python analysis/async_tail.py --family payment
    python analysis/async_tail.py --write-doc     # refresh docs/ASYNC_TAIL.md
"""
import argparse
import collections
import io
import os
import re

DUMP = 'analysis/ida_strings.txt'
SRC = 'replica/src'
DOC = 'docs/ASYNC_TAIL.md'

SM = re.compile(r'<([A-Za-z_][A-Za-z0-9_]*)>d__(\d+)')

PAYMENT_WORDS = (
    'pay', 'checkout', 'order', 'card', '3ds', 'threed', 'stripe', 'paypal', 'adyen', 'unzer',
    'cardinal', 'checkoutcom', 'mollie', 'midtrans', 'omise', 'sibs', 'paynamics', 'gmo',
    'commercehub', 'square', 'touchtech', 'komoju', 'klarna', 'braintree', 'authorize', 'capture',
    'token', 'refund', 'void', 'charge', 'intent', 'challenge', 'acs', 'issuer', 'cres', 'pares',
)
STORE_WORDS = (
    'cart', 'product', 'shop', 'stock', 'variant', 'addtocart', 'checkstock', 'findproduct',
    'home', 'login', 'account', 'address', 'shipping', 'queue', 'captcha', 'antibot', 'proxy',
)


def family_of(name: str) -> str:
    low = name.lower()
    if any(w in low for w in PAYMENT_WORDS):
        return 'payment'
    if any(w in low for w in STORE_WORDS):
        return 'store'
    return 'other'


def image_names():
    counts = collections.Counter()
    for line in io.open(DUMP, encoding='utf-8', errors='replace'):
        if '\t' not in line:
            continue
        _, text = line.split('\t', 1)
        m = SM.search(text)
        if m:
            counts[m.group(1)] += 1
    return counts


def replica_sources():
    texts = []
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if name.endswith('.cs'):
                texts.append(io.open(os.path.join(root, name), encoding='utf-8', errors='replace').read())
    return '\n'.join(texts)


def spellings_of(name: str):
    """Every spelling of a name this comparison should accept, in one place.

    Three things differ between the image and the replica and none of them is behaviour:
      - the Async suffix (`Login` vs `LoginAsync`);
      - digits versus words for the protocol (`ProcessThreeDs` vs `Process3DSAsync`);
      - and that is where it stops. Anything else is a real difference and should show up as absent.
    """
    out = {name}
    if name.endswith('Async'):
        out.add(name[:-5])
    else:
        out.add(name + 'Async')

    extra = set()
    for s in out:
        extra.add(s.replace('3DS', 'ThreeDS'))
        extra.add(s.replace('ThreeDS', '3DS').replace('ThreeDs', '3DS'))
    return out | extra


def classify(names, source):
    """Three states per image name: declared, only mentioned, absent.

    The first version compared the bare identifier only and reported 723 of 801 missing -- a naming
    figure wearing a gap figure's clothes: the image's state machine for an async method called `Login`
    is `<Login>d__25` while the replica writes `LoginAsync`. The second version allowed the Async suffix
    to differ, but still had only two states, so `ContinueUnzerThreeDs` -- which the replica names in a
    doc comment while implementing the behaviour as `RunUnzerThreeDsAsync` -- read as absent. And
    `ProcessThreeDs` stayed absent even after both fixes until the digit/word spelling was tried too.

    So the answer is not a boolean. `declared` means a method of that name exists; `mentioned` means the
    name appears in the source but not as a declaration, which usually means the behaviour lives under
    a different name and the doc says which; `absent` means no spelling occurs at all, and that is the
    only class that is a candidate for a coverage gap.
    """
    declared, mentioned, absent = [], [], []
    for name in sorted(names):
        variants = spellings_of(name)
        if any(re.search(r'\b' + re.escape(s) + r'\s*\(', source) for s in variants):
            declared.append(name)
        elif any(s in source for s in variants):
            mentioned.append(name)
        else:
            absent.append(name)
    return declared, mentioned, absent


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', choices=['payment', 'store', 'other', 'all'], default='all')
    ap.add_argument('--write-doc', action='store_true')
    args = ap.parse_args(argv)

    counts = image_names()
    source = replica_sources()
    declared, mentioned, absent = classify(counts, source)

    fam = collections.Counter(family_of(n) for n in counts)
    miss_fam = collections.Counter(family_of(n) for n in absent)

    print('image async state-machine names   : %d (occurrences %d)' % (len(counts), sum(counts.values())))
    print('  declared in replica             : %d' % len(declared))
    print('  named but not declared          : %d' % len(mentioned))
    print('  absent from replica source      : %d   <- the only class that is a coverage gap' % len(absent))
    print('by family (image / absent):')
    for key in ('payment', 'store', 'other'):
        print('  %-8s %4d / %4d' % (key, fam.get(key, 0), miss_fam.get(key, 0)))

    selected = [n for n in absent if args.family == 'all' or family_of(n) == args.family]
    print('\nabsent (%s, %d):' % (args.family, len(selected)))
    for n in selected:
        print('  %-50s occ=%d family=%s' % (n, counts[n], family_of(n)))
    if args.family != 'all':
        named = [n for n in mentioned if family_of(n) == args.family]
        print('\nnamed-but-not-declared in the same family (%d) — check the doc mention before calling these gaps:' % len(named))
        for n in named:
            print('  %s' % n)

    if args.write_doc:
        lines = [
            '# 异步状态机长尾（由 `python analysis/async_tail.py --write-doc` 生成）',
            '',
            '> 镜像的 NativeAOT 产物仍保留 `<名字>d__NN` 状态机串。三态判定：**declared**（复刻件有同名方法）、',
            '> **mentioned**（源码里出现过这个名字但不是声明——通常是行为换名实现了、文档里点了名）、',
            '> **absent**（源码里根本没出现，**只有这一类才算覆盖缺口**）。',
            '',
            '| 项 | 值 |',
            '|---|---|',
            '| 镜像异步状态机名 | %d（出现 %d 次） |' % (len(counts), sum(counts.values())),
            '| declared | %d |' % len(declared),
            '| mentioned | %d |' % len(mentioned),
            '| **absent** | **%d** |' % len(absent),
            '',
            '## 按家族（镜像 / absent）',
            '',
            '| 家族 | 镜像 | absent |',
            '|---|---|---|',
        ]
        for key in ('payment', 'store', 'other'):
            lines.append('| %s | %d | %d |' % (key, fam.get(key, 0), miss_fam.get(key, 0)))
        lines += ['', '## payment 家族 · absent（真正的缺口）', '', '| 名字 | 出现 |', '|---|---|']
        for n in [m for m in absent if family_of(m) == 'payment']:
            lines.append('| `%s` | %d |' % (n, counts[n]))
        lines += ['', '## payment 家族 · mentioned（换名实现或只是文档点名）', '', '| 名字 |', '|---|']
        for n in [m for m in mentioned if family_of(m) == 'payment']:
            lines.append('| `%s` |' % n)
        lines += ['', '## store 家族 · absent', '', '| 名字 | 出现 |', '|---|---|']
        for n in [m for m in absent if family_of(m) == 'store']:
            lines.append('| `%s` | %d |' % (n, counts[n]))
        lines += ['', '> `other` 家族 absent %d 个：`python analysis/async_tail.py --family other`。' % miss_fam.get('other', 0), '']
        io.open(DOC, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
        print('\nwrote %s' % DOC)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(__import__('sys').argv[1:]))
