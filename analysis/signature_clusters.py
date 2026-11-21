"""Cluster block A's leftovers by signature, not by address.

R1349 showed the address range holds three families. The remaining documents in it can be sorted the same way
without reading a single sender: a document's declared variables are its signature, and the three known families
each have one.

    Storefront       $lines/$buyerIdentity/$attributes/$country/$language, $cartId/$lineItemId/$version, $input + include*
    tm-api           $action: SetCart*!, $locale, $preferredLocale
    Shop app         $brokerId/$key/$searchKind

This decodes each remaining document, prints its declared set, and says which known family it matches — or that it
matches none.

Usage: python analysis/signature_clusters.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SITES = {
    'cartCreate': 0x1470F23FC,
    'checkoutAsGuest': 0x1470F24CC,
    'createCartByStore': 0x1470F32D4,
    'createCheckoutPayment': 0x1470F3BEC,
    'createMyPayment': 0x1470F3DC4,
    'customerAccessTokenCreate': 0x1470F41B4,
    'getProductDetails': 0x1470F43C4,
    'initiateCheckout': 0x1470F489C,
    'maintainShippingGroups': 0x1470F4AAC,
    'saveAddress': 0x1470F58BC,
    'createCheckout': 0x1470F3634,
}
OUT = 'analysis/.block_a_docs.json'

FAMILIES = {
    'Storefront': {
        'tokens': {'lines', 'buyerIdentity', 'attributes', 'country', 'language', 'cartId', 'lineItemId',
                   'version', 'quantity', 'input', 'includeInventory', 'metafieldsIdentifiers',
                   'customerAccessToken'},
    },
    'tm-api': {'tokens': {'action', 'locale', 'preferredLocale'}},
    'Shop-app': {'tokens': {'brokerId', 'key', 'searchKind', 'filter', 'first'}},
}


def bytes_at(address, size):
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


documents = {}
for name, address in SITES.items():
    text = read_string(address)
    documents[name] = text
    declared = set(re.findall(r'\$(\w+)\s*:', text))
    scores = {family: len(declared & spec['tokens']) for family, spec in FAMILIES.items()}
    best = max(scores, key=scores.get)
    verdict = best if scores[best] >= 2 else 'none'
    print('%-26s %5d chars  %-11s %s' % (name, len(text), verdict, sorted(declared)))

io.open(OUT, 'w', encoding='utf-8', newline='').write(
    json.dumps(documents, ensure_ascii=False, indent=1, sort_keys=True))
print('wrote %s' % OUT)
