"""R1367: three more host-less operations join the session family, on the same basis R1359 used.

The five "needs a capture" documents are not all alike. getCart and saveAddress are already carried (R1359, R1366),
so the open-items list was stale on two rows. Of the rest, createMyPayment belongs with the Cybersource family R1364
identified — updateMyPaymentWithActions in the same block names cybersource and isv_* fields — so it stays out.

That leaves createCartByStore, initiateCheckout and maintainShippingGroups: no host, envelope-only handlers, and the
same block as the four operations R1359 landed the same way. They join StoreSessionQueries, origin from the caller.

A caution gets written down too: matching these documents against known families by a single variable name produced
"matches" (key -> shop app, locale -> tm-api) that are overlaps of one token. That is exactly the false positive
R1350 warned about, so no host is inferred from it.

Usage: python analysis/add_session_three.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

TARGETS = {
    'createCartByStore': (0x1470F32D4, 'CreateCartByStoreDocument'),
    'initiateCheckout': (0x1470F489C, 'InitiateCheckoutDocument'),
    'maintainShippingGroups': (0x1470F4AAC, 'MaintainShippingGroupsDocument'),
}
PATH = 'replica/src/Cybersole.Stores/Flows/StoreSessionQueries.cs'
DOCS = 'analysis/.block_a_docs.json'


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


documents = {}
for name, (address, _) in TARGETS.items():
    documents[name] = read_string(address)
    declared = sorted(set(re.findall(r'\$(\w+)\s*:', documents[name])))
    print('%-24s %5d chars  declares %s' % (name, len(documents[name]), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
for name, text in documents.items():
    docs['session_' + name] = text
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

path = io.open(PATH, encoding='utf-8', newline='').read()
anchor_line = [line for line in path.splitlines()
               if line.strip() == '/// saveAddress, 296 characters from 0x1470F58BC. The image\'s own async tail names a SaveAddress step, which is']
if len(anchor_line) != 1:
    raise SystemExit('anchor matched %d times' % len(anchor_line))

blocks = []
rows = []
cases = []
for name, (address, constant) in TARGETS.items():
    text = documents[name]
    declared = sorted(set(re.findall(r'\$(\w+)\s*:', text)))
    blocks.append('''    /// <summary>%s, %d characters from %#x.</summary>
    public const string %s = "%s";
''' % (name, len(text), address, constant, escape_literal(text)))
    rows.append('        ["%s"] = %s,' % (
        name,
        'new[] { ' + ', '.join('"%s"' % n for n in declared) + ' }' if declared else 'Array.Empty<string>()'))
    cases.append('        "%s" => %s,' % (name, constant))

insert = '\n'.join(blocks) + '\n'
path = path.replace(anchor_line[0], insert + anchor_line[0], 1)

row_anchor = '["saveAddress"] = new[] {'
position = path.find(row_anchor)
end_of_row = path.find('\n', position)
path = path[:end_of_row] + '\n' + '\n'.join(rows) + path[end_of_row:]

switch_anchor = '        "saveAddress" => SaveAddressDocument,'
if path.count(switch_anchor) != 1:
    raise SystemExit('switch anchor matched %d times' % path.count(switch_anchor))
path = path.replace(switch_anchor, switch_anchor + '\n' + '\n'.join(cases))

io.open(PATH, 'w', encoding='utf-8', newline='').write(path)
print('three operations added to the session family')
