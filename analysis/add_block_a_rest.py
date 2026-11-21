"""R1352: four of the last seven are placeable — two Storefront (in two API versions), one more product-drops,
and one that names a store outright.

The seven remaining block-A documents, scanned for their senders:

    cartCreate                 api/2021-10/graphql.json                              Storefront, 2021-10
    customerAccessTokenCreate  api/2025-04/graphql.json                              Storefront, 2025-04
    createCheckout             apps/product-drops?kind=mutation&operation=createCheckout   product-drops
    checkoutAsGuest            https://www.on.com/ko-kr/graphql                     On Running, ko-kr
    createCartByStore          no host, no path
    createMyPayment            no host, no path
    initiateCheckout           no host, no path

Two things stand out. The Storefront operations do not share one API version — cartCreate pins 2021-10 while
customerAccessTokenCreate pins 2025-04 — so the version is per operation, not per store, and the class has to keep
each one's own. And checkoutAsGuest carries a full host with a locale path, which is the first time in this range a
sender has named its store: www.on.com, Korean storefront.

Usage: python analysis/add_block_a_rest.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

DOCS = 'analysis/.block_a_docs.json'
STOREFRONT = 'replica/src/Cybersole.Stores/Flows/ShopifyStorefrontQueries.cs'
DROPS = 'replica/src/Cybersole.Stores/Flows/ShopifyProductDrops.cs'


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


def escape_literal(text):
    out = []
    for character in text:
        if character == '\\':
            out.append('\\\\')
        elif character == '"':
            out.append('\\"')
        elif character == '\r':
            out.append('\\r')
        elif character == '\n':
            out.append('\\n')
        elif character == '\t':
            out.append('\\t')
        else:
            out.append(character)
    return ''.join(out)


existing = json.loads(io.open(DOCS, encoding='utf-8').read())
documents = {
    'cart_create': read_string(0x1470F23FC),
    'customer_access_token_create': read_string(0x1470F41B4),
    'create_checkout': read_string(0x1470F3634),
    'checkout_as_guest': read_string(0x1470F24CC),
}
for name, text in documents.items():
    print('%-30s %4d chars  %s' % (name, len(text), text[:60].replace('\n', ' ').replace('\r', '')))
existing.update(documents)
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(existing, ensure_ascii=False, indent=1, sort_keys=True))

# --- Storefront: two more operations, each pinning its own API version -------------------------------
text = io.open(STOREFRONT, encoding='utf-8', newline='').read()
if 'CustomerAccessTokenCreate' in text:
    raise SystemExit('storefront already extended')

anchor = '    /// <summary>The variables each document declares.</summary>'
if text.count(anchor) != 1:
    raise SystemExit('storefront anchor found %d times' % text.count(anchor))

constants = '''    /// <summary>cartCreate, 91 characters from 0x1470F23FC — its sender pins API version 2021-10.</summary>
    public const string CartCreate = "%s";

    /// <summary>The version cartCreate's sender uses; the other two pin 2025-04, so the version is per call.</summary>
    public const string CartCreateApiVersion = "2021-10";

    /// <summary>customerAccessTokenCreate, 250 characters from 0x1470F41B4, on API version 2025-04.</summary>
    public const string CustomerAccessTokenCreate = "%s";

''' % (escape_literal(documents['cart_create']), escape_literal(documents['customer_access_token_create']))

text = text.replace(anchor, constants + anchor)

# Declared sets for the two new operations.
declared_anchor = '''        ["removeLineItemFromCart"] = new[] { "cartId", "lineItemId", "version", "quantity", "locale" },'''
if text.count(declared_anchor) != 2:
    raise SystemExit('declared rows found %d times' % text.count(declared_anchor))

first = text.find(declared_anchor)
text = (text[:first + len(declared_anchor)] +
        '\n        ["cartCreate"] = new[] { "input", "buyerIdentity", "country", "language" },' +
        '\n        ["customerAccessTokenCreate"] = new[] { "input" },' +
        text[first + len(declared_anchor):])

second = text.find(declared_anchor, first + 1)
text = (text[:second + len(declared_anchor)] +
        '\n        ["cartCreate"] = new[] { "input" },' +
        '\n        ["customerAccessTokenCreate"] = new[] { "input" },' +
        text[second + len(declared_anchor):])

switch_anchor = '''        "removeLineItemFromCart" => RemoveLineItemFromCart,'''
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor found %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor +
                    '\n        "cartCreate" => CartCreate,' +
                    '\n        "customerAccessTokenCreate" => CustomerAccessTokenCreate,')
io.open(STOREFRONT, 'w', encoding='utf-8', newline='').write(text)
print('storefront gained cartCreate and customerAccessTokenCreate')

# --- Product drops: createCheckout uses the same path with a different operation --------------------
drops = io.open(DROPS, encoding='utf-8', newline='').read()
if 'CreateCheckout' in drops:
    raise SystemExit('drops already extended')

drops = drops.replace(
    '    public const string Path = "apps/product-drops?kind=mutation&operation=getProductDetails";',
    '    public const string Path = "apps/product-drops?kind=mutation&operation=getProductDetails";\n\n'
    '    /// <summary>The path the createCheckout sender builds — same app, its own operation.</summary>\n'
    '    public const string CheckoutPath = "apps/product-drops?kind=mutation&operation=createCheckout";\n\n'
    '    /// <summary>createCheckout, 720 characters from 0x1470F3634.</summary>\n'
    '    public const string CreateCheckoutDocument =\n'
    '        "%s";' % escape_literal(documents['create_checkout']))

io.open(DROPS, 'w', encoding='utf-8', newline='').write(drops)
print('product drops gained createCheckout')
