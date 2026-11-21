"""R1364: updateShipAddress belongs to the hash family, and updateMyPaymentWithActions names a payment provider.

updateShipAddress's handler (sub_14088C350) carries x-graphql-hash and two more 64-hex values beside the cookie and
browser headers — the block where queries travel by hash (R1357). Its document declares $address, so it goes into
GraphQlHashQueries with the other three.

updateMyPaymentWithActions' handler (sub_140E55A00) is a different animal entirely: createMyPayment,
creditCardWithPayerAuthentication, cybersource, isv_payment_data, isv_screenHeight, isv_screenWidth, isv_store,
isv_customerIpAddress, amount, centAmount, currencyCode, customFields and "No capture context". Cybersource's ISV
fields and the "no capture context" refusal belong to a payment provider this replica does not implement, and the
family's other operation (createMyPayment) sits in the same block. Recorded, not invented.

Usage: python analysis/add_hash_update_ship_address.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470FD394
PATH = 'replica/src/Cybersole.Stores/Flows/GraphQlHashQueries.cs'
DOCS = 'analysis/.hash_family_docs.json'


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
print('updateShipAddress: %d chars  declares %s' % (len(document), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['update_ship_address'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'UpdateShipAddress' in text:
    raise SystemExit('already present')

anchor_line = [line for line in text.splitlines()
               if line.strip().startswith('/// <summary>GetCart, 3520 characters')]
if len(anchor_line) != 1:
    raise SystemExit('anchor line matched %d times' % len(anchor_line))

constants = '''    /// <summary>updateShipAddress, %d characters from 0x1470FD394.</summary>
    public const string UpdateShipAddressDocument = "%s";

''' % (len(document), escape_literal(document))

text = text.replace(anchor_line[0], constants + anchor_line[0], 1)

switch_anchor = '        "GetCart" => GetCartDocument,'
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor matched %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor + '\n        "updateShipAddress" => UpdateShipAddressDocument,')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('updateShipAddress added to the hash family')
