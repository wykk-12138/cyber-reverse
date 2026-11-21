"""R1366: saveAddress joins the session family, and the async tail gets written down with its limits.

The store-family async tail (analysis/async_tail.py --family store) names 34 steps the replica has no method for.
Probing three of them by name produced nothing usable: GetCartId, GetCartCsrf and GetCartItemId exist only as
<Name>d__NN state-machine strings, and R1353 already established that following those leads to metadata rather than
code. So the tail is recorded as a list with its limits, not chased by name.

What can be done with evidence is saveAddress: the document is 296 characters and declares $address, $editAddress,
$saveAddress and $setDefault, and it belongs with the host-less session operations. The tail's own SaveAddress name
corroborates that the image has such a step.

Usage: python analysis/add_session_save_address.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470F58BC
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


document = read_string(SOURCE)
declared = sorted(set(re.findall(r'\$(\w+)\s*:', document)))
print('saveAddress: %d chars  declares %s' % (len(document), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['save_address'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'SaveAddressDocument' in text:
    raise SystemExit('already present')

anchor_line = [line for line in text.splitlines()
               if line.strip() == '/// <summary>getCart, 3234 characters from 0x14714361C.</summary>']
if len(anchor_line) != 1:
    raise SystemExit('anchor matched %d times' % len(anchor_line))

block = '''    /// <summary>
    /// saveAddress, %d characters from 0x1470F58BC. The image's own async tail names a SaveAddress step, which is
    /// what corroborates it as a store step rather than a helper.
    /// </summary>
    public const string SaveAddressDocument = "%s";

''' % (len(document), escape_literal(document))

text = text.replace(anchor_line[0], block + anchor_line[0], 1)

row = '\n        ["saveAddress"] = new[] { %s },' % ', '.join('"%s"' % n for n in declared)
declared_anchor = '["UpdateContactDetails"] = new[] {'
position = text.find(declared_anchor)
end_of_row = text.find('\n', position)
text = text[:end_of_row] + row + text[end_of_row:]

switch_anchor = '        "UpdateContactDetails" => UpdateContactDetailsDocument,'
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor matched %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor + '\n        "saveAddress" => SaveAddressDocument,')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('saveAddress added to the session family')
