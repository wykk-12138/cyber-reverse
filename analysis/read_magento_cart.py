"""Read the Magento cart documents the image carries, as UTF-16, and write them out for the source.

The strings are UTF-16 in the image (the first three words of every listing gave that away -- 0x6D0075 00
pairs), so they have to be decoded rather than copied. This decodes each one, prints it with its escapes
visible, and saves the exact characters so the C# literal can be generated without transcription.

Usage: python analysis/read_magento_cart.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SITES = {
    'add_products': 0x1470FD624,
    'create_empty': 0x1470FD4C4,
    'customer_cart': 0x14718FB74,
    # R1321: the rest of the frozen GraphQL documents found in the same sweep.
    'add_billing_address': 0x1470E4F94,
    'approve_member_payment': 0x1470E9FA4,
    'add_to_cart_query': 0x14713DE4C,
    'buynow': 0x14713E034,
}
OUT = 'analysis/.magento_cart_docs.json'


def read_string(chars_va):
    """Decode the UTF-16 string at chars_va, using the 4-byte length in the object header."""
    res = call('get_bytes', {'regions': [{'addr': hex(chars_va - 12), 'size': 12}]})
    if isinstance(res, str):
        res = json.loads(res)
    header = bytes(int(t, 16) for t in res[0]['data'].split())
    length = int.from_bytes(header[8:12], 'little')

    res = call('get_bytes', {'regions': [{'addr': hex(chars_va), 'size': max(2, length * 2)}]})
    if isinstance(res, str):
        res = json.loads(res)
    body = bytes(int(t, 16) for t in res[0]['data'].split())
    return body.decode('utf-16-le', errors='replace'), length


def main():
    found = {}
    for name, chars_va in SITES.items():
        text, declared = read_string(chars_va)
        found[name] = text
        print('=== %s @ 0x%X  declared length %d, decoded %d chars' % (name, chars_va, declared, len(text)))
        print(text.encode('unicode_escape').decode('ascii'))
        print()
    io.open(OUT, 'w', encoding='utf-8', newline='').write(json.dumps(found, ensure_ascii=False, indent=2))
    print('wrote %s' % OUT)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
