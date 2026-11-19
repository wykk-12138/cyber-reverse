"""Triage the payment-name queue into three honest buckets by asking whether the replica already speaks the gateway.

The rule comes from R1226: derive the gateway a name belongs to, then look for that gateway's host in replica/src.
A host that is present means the behaviour probably exists under another name, which the goal permits; a host that
is absent makes the name a candidate for the four-step chain; a name that implies no gateway cannot be decided this
way and is reported as undecided rather than guessed.

Usage:
    python analysis/triage_payment_names.py
"""
import glob
import io
import json
import re

GATEWAYS = {
    'unzer': 'api.unzer.com',
    'adyen': 'adyen.com',
    'paypal': 'paypal.com',
    'square': 'squareup.com',
    'midtrans': 'api.midtrans.com',
    'stripe': 'api.stripe.com',
    'cardinal': 'cardinalcommerce.com',
    'omise': 'omise.co',
    'mollie': 'mollie.com',
    'gmo': 'gmo-pg.com',
    'sibs': 'sibs',
    'paynamics': 'paynamics',
    'touchtech': 'touchtech',
    'commercehub': 'commercehub',
}


def main():
    src = {}
    for path in glob.glob('replica/src/**/*.cs', recursive=True):
        try:
            src[path] = io.open(path, encoding='utf-8', errors='replace').read()
        except OSError:
            pass
    corpus = '\n'.join(src.values())

    names = []
    section = 0
    for line in io.open('analysis/payment_name_gaps.txt', encoding='utf-8').read().split('\n'):
        if line.startswith('# SECTION 2'):
            section = 2
            continue
        if section == 2 and line and not line.startswith('#'):
            names.append(line.split('\t')[0])

    present, absent, undecided = [], [], []
    for name in names:
        low = name.lower()
        hit = next((g for g in GATEWAYS if g in low), None)
        if hit is None:
            undecided.append(name)
        elif GATEWAYS[hit] in corpus:
            present.append((name, GATEWAYS[hit]))
        else:
            absent.append((name, GATEWAYS[hit]))

    out = 'analysis/payment_name_triage.txt'
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Triage of SECTION 2 of payment_name_gaps.txt, by gateway host presence in replica/src.\n')
        f.write('# Rule: name -> gateway -> is that gateway host already spoken in src?\n')
        f.write('# present  = the behaviour probably exists under another name (renaming is allowed)\n')
        f.write('# absent   = candidate for the four-step chain\n')
        f.write('# undecided= the name implies no gateway, so this test cannot answer\n')
        f.write('# Regenerate with: python analysis/triage_payment_names.py\n\n')
        f.write('# GATEWAY HOST PRESENT (%d)\n' % len(present))
        for n, host in present:
            f.write('%-42s\t%s\n' % (n, host))
        f.write('\n# GATEWAY HOST ABSENT - candidates (%d)\n' % len(absent))
        for n, host in absent:
            f.write('%-42s\t%s\n' % (n, host))
        f.write('\n# NO GATEWAY IN THE NAME - undecided (%d)\n' % len(undecided))
        for n in undecided:
            f.write('%s\n' % n)

    print('names considered: %d' % len(names))
    print('  gateway host present : %d' % len(present))
    print('  gateway host absent  : %d' % len(absent))
    print('  undecided            : %d' % len(undecided))
    print('wrote', out)
    print('\ncandidates:')
    for n, host in absent[:20]:
        print('   %-40s needs %s' % (n, host))


if __name__ == '__main__':
    main()
