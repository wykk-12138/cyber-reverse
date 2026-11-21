"""R1361: UpdateShippingAddress joins the api/graphql family — its second handler is that endpoint.

The operation name has two references. One is sub_14098C830, which posts to
/scapi/ShopperBaskets/updateShippingAddressForShipment — Salesforce's Commerce API, a different transport for a
similar idea. The other is sub_140E1DD80, which builds api/graphql with the address fields (firstName, lastName,
address1, address2, city, countryCode, phone) and the label "Submit info".

api/graphql is the relative path four other operations already use (R1346), so this one joins StorefrontApiQueries
rather than inventing a class for it. The SCAPI handler is recorded in the docs and not implemented: it belongs to a
commercial platform surface nothing else in the replica touches.

Usage: python analysis/add_storefront_update_shipping.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470E3CD4
PATH = 'replica/src/Cybersole.Stores/Flows/StorefrontApiQueries.cs'
DOCS = 'analysis/.storefront_api_docs.json'


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


document = read_string(SOURCE)
declared = sorted(set(re.findall(r'\$(\w+)\s*:', document)))
print('UpdateShippingAddress: %d chars  declares %s' % (len(document), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['update_shipping_address'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'UpdateShippingAddress' in text:
    raise SystemExit('already present')

anchor = '    /// <summary>The session query, 133 characters at 0x147146994.</summary>'
if text.count(anchor) != 1:
    raise SystemExit('constant anchor found %d times' % text.count(anchor))

constants = '''    /// <summary>UpdateShippingAddress, %d characters from 0x1470E3CD4.</summary>
    public const string UpdateShippingAddress = "%s";

''' % (len(document), escape_literal(document))

text = text.replace(anchor, constants + anchor)

declared_anchor = '''        ["getSession"] = Array.Empty<string>(),'''
if text.count(declared_anchor) != 2:
    raise SystemExit('declared rows found %d times' % text.count(declared_anchor))

first = text.find(declared_anchor)
row = '\n        ["UpdateShippingAddress"] = new[] { %s },' % ', '.join('"%s"' % n for n in declared)
text = text[:first + len(declared_anchor)] + row + text[first + len(declared_anchor):]

second = text.find(declared_anchor, first + 1)
text = text[:second + len(declared_anchor)] + row + text[second + len(declared_anchor):]

switch_anchor = '''        "getSession" => Session,'''
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor found %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor + '\n        "UpdateShippingAddress" => UpdateShippingAddress,')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('UpdateShippingAddress added to the api/graphql family')
