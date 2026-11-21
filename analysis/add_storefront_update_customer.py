"""R1362: UpdateCustomerForCart joins api/graphql too; updateShipAddress sits in the hash family's block.

UpdateCustomerForCart's handler (sub_140E1D030) builds api/graphql with basketId, email and input — the same relative
path five other operations now use — so its document joins StorefrontApiQueries.

updateShipAddress's handler (sub_14088C350) carries a Sentry trace header and */*, and sits in the 0x14088xxxx block
where GetCartCookie's handler lives and where queries travel by hash (R1357). Its declared variable is $address. That
is recorded rather than implemented: "same block as the hash family" is a lead, and R1347 already showed a block can
hold families that are not related.

Usage: python analysis/add_storefront_update_customer.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470E39BC
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
print('UpdateCustomerForCart: %d chars  declares %s' % (len(document), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['update_customer_for_cart'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'UpdateCustomerForCart' in text:
    raise SystemExit('already present')

# Copy the anchor out of the source instead of retyping it (R1361's lesson).
anchor_line = [line for line in text.splitlines()
               if line.strip().startswith('/// <summary>UpdateShippingAddress')]
if len(anchor_line) != 1:
    raise SystemExit('anchor line matched %d times' % len(anchor_line))
anchor = anchor_line[0]

constants = '''    /// <summary>UpdateCustomerForCart, %d characters from 0x1470E39BC.</summary>
    public const string UpdateCustomerForCart = "%s";

''' % (len(document), escape_literal(document))

text = text.replace(anchor, constants + anchor, 1)

declared_anchor = '["UpdateShippingAddress"] = new[] {'
if text.count(declared_anchor) != 2:
    raise SystemExit('declared rows found %d times' % text.count(declared_anchor))
row = '\n        ["UpdateCustomerForCart"] = new[] { %s },' % ', '.join('"%s"' % n for n in declared)
first = text.find(declared_anchor)
end_of_row = text.find('\n', first)
text = text[:end_of_row] + row + text[end_of_row:]
second = text.find(declared_anchor, end_of_row)
end_of_second = text.find('\n', second)
text = text[:end_of_second] + row + text[end_of_second:]

switch_anchor = '        "UpdateShippingAddress" => UpdateShippingAddress,'
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor found %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor + '\n        "UpdateCustomerForCart" => UpdateCustomerForCart,')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('UpdateCustomerForCart added')
