"""R1362b: addToCartByChannel belongs to the session family — its handler's variable set says so.

The handler sub_140E53A10 carries cartId, key, locale, productId, quantity, country and address, and no host. key and
locale are exactly what getCart declares in the same family, and the block is the 0x140E5xxxx one that R1359 placed
there. So the document joins StoreSessionQueries rather than getting its own origin rule.

Usage: python analysis/add_session_add_to_cart.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470E8DCC
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
print('addToCartByChannel: %d chars  declares %s' % (len(document), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['add_to_cart_by_channel'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'AddToCartByChannel' in text:
    raise SystemExit('already present')

anchor_line = [line for line in text.splitlines()
               if line.strip().startswith('/// <summary>getCart, 3234 characters')]
if len(anchor_line) != 1:
    raise SystemExit('anchor line matched %d times' % len(anchor_line))

constants = '''    /// <summary>addToCartByChannel, %d characters from 0x1470E8DCC.</summary>
    public const string AddToCartByChannelDocument = "%s";

''' % (len(document), escape_literal(document))

text = text.replace(anchor_line[0], constants + anchor_line[0], 1)

declared_anchor = '        ["getCart"] = new[] { "key", "locale" },'
count = text.count(declared_anchor)
if count not in (1, 2):
    raise SystemExit('declared rows found %d times' % count)
row = '\n        ["addToCartByChannel"] = new[] { %s },' % ', '.join('"%s"' % n for n in declared)
for index in range(count):
    position = text.find(declared_anchor)
    text = text[:position + len(declared_anchor)] + row + text[position + len(declared_anchor):]
    declared_anchor_local = declared_anchor

switch_anchor = '        "getCart" => GetCartDocument,'
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor found %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor + '\n        "addToCartByChannel" => AddToCartByChannelDocument,')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('addToCartByChannel added to the session family')
