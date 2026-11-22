"""R1381: the payment tail, tested the way the store tail was — before assuming it behaves the same.

R1367 tried all thirty store-family names and found twenty-nine existed only as `<Name>d__NN` state-machine strings and
the one with a standalone string had no references. The payment family has sixty-four names in the same report and was
never put through that test; assuming the answer would be the same is exactly the kind of inheritance this project keeps
paying for.

For each name: does an exact standalone string exist, and if so does any code reference it? A name that passes both is
followable to a handler; a name that fails either is not, and says so.

Usage: python analysis/classify_payment_tail.py
"""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'analysis')

from pe_read_direct import Image, find_disp32  # noqa: E402

DUMP = 'analysis/ida_strings.txt'
IMAGE = 'target/Cybersole.exe'

PAYMENT_WORDS = (
    'pay', 'checkout', 'order', 'card', '3ds', 'threed', 'stripe', 'paypal', 'adyen', 'unzer',
    'cardinal', 'checkoutcom', 'mollie', 'midtrans', 'omise', 'sibs', 'paynamics', 'gmo',
    'commercehub', 'square', 'touchtech', 'komoju', 'klarna', 'braintree', 'authorize', 'capture',
    'token', 'refund', 'void', 'charge', 'intent', 'challenge', 'acs', 'issuer', 'cres', 'pares',
)

STATE_MACHINE = re.compile(r'<([A-Za-z_][A-Za-z0-9_]*)>d__\d+')


def payment_names():
    names = set()
    for line in io.open(DUMP, encoding='utf-8', errors='replace'):
        for match in STATE_MACHINE.finditer(line):
            name = match.group(1)
            if any(word in name.lower() for word in PAYMENT_WORDS):
                names.add(name)
    return sorted(names)


def exact_strings():
    found = {}
    for line in io.open(DUMP, encoding='utf-8', errors='replace'):
        parts = line.rstrip('\n').split('\t', 1)
        if len(parts) != 2:
            continue
        text = parts[1].strip()
        if 4 <= len(text) <= 60 and text not in found:
            found[text] = int(parts[0], 16)
    return found


def main():
    image = Image(IMAGE)
    names = payment_names()
    pool = exact_strings()

    followable, metadata_only = [], []
    for name in names:
        address = pool.get(name)
        if address is None:
            metadata_only.append((name, 'no standalone string'))
            continue

        hits = find_disp32(image, address - 12) + find_disp32(image, address)
        if hits:
            followable.append((name, address, hits[0]))
        else:
            metadata_only.append((name, 'standalone string, no reference'))

    print('payment-family async names: %d' % len(names))
    print('  followable to a handler: %d' % len(followable))
    print('  metadata only:           %d' % len(metadata_only))
    print()

    for name, address, site in followable:
        print('  %-44s str %#x  first site %#x  func %s' % (
            name, address, site, ('%#x' % image.function_start(site)) if image.function_start(site) else '?'))

    print()
    print('metadata-only names (first 20):')
    for name, reason in metadata_only[:20]:
        print('  %-44s %s' % (name, reason))

    record = {
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
