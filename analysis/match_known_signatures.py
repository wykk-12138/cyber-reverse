"""Do any of the five host-less documents match a family whose host is already known?

The five that need a capture were classified as "no host, no path". But a document's own variables can still place it:
the Shop app family keys everything on brokerId (server.shop.app), the tm-api family on an action object plus two
locales, and the Storefront family on lines/cartId/version. If one of these declarations matches, the host is known
even though the sender never named it.

Usage: python analysis/match_known_signatures.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DOCS = {
    'getCart': 0x14714361C,
    'createCartByStore': 0x1470F32D4,
    'createMyPayment': 0x1470F3DC4,
    'initiateCheckout': 0x1470F489C,
    'maintainShippingGroups': 0x1470F4AA0 + 12,
}

FAMILIES = {
    'shop-app (server.shop.app)': {'brokerId', 'key', 'searchKind', 'variantsLimit', 'sortReviewsBy'},
    'tm-api (action + locales)': {'action', 'locale', 'preferredLocale'},
    'caption-storefront (lines/cartId/version)': {'lines', 'cartId', 'version', 'buyerIdentity', 'quantity'},
    'braintree (client/creditCard)': {'client', 'creditCard', 'clientSdkMetadata', 'authorizationFingerprint'},
}


def bytes_at(address, size):
    sys.path.insert(0, 'analysis')
    from ida import call
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        try:
            reply = json.loads(reply)
        except json.JSONDecodeError:
            reply = json.loads(reply.splitlines()[0])
    if isinstance(reply, dict):
        reply = reply.get('result', reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


def read_string(chars_va):
    length = int.from_bytes(bytes_at(chars_va - 12, 12)[8:12], 'little')
    chunks = []
    offset = 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


for name, address in DOCS.items():
    text = read_string(address)
    declared = set(re.findall(r'\$(\w+)\s*:', text))
    scores = {family: len(declared & tokens) for family, tokens in FAMILIES.items()}
    best = max(scores, key=scores.get)
    verdict = best if scores[best] >= 1 else 'no match'
    print('%-24s %5d chars  declared=%-58s -> %s' % (name, len(text), sorted(declared), verdict))
