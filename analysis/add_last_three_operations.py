"""R1377: three operations were still absent, and my "64 of 65" was reading the wrong number.

operation_gap.py prints two different counts: how many operation names the replica declares (64), and how many of the
image's 65 the replica actually carries. I reported the first as if it were the second, so "64/65, one left" was wrong
by two operations.

The tool now prints the ratio explicitly, and this lands the three that were really absent — SignInAsGuest (453),
addToCart (232) and buynow (216) — in the session family, whose rule is that the origin is the caller's.

Usage: python analysis/add_last_three_operations.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

ABSENT = {
    'SignInAsGuest': 0x1470E1ADC,
    'addToCart': 0x14713de4c,
    'buynow': 0x14713e034,
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
    chunks, offset = [], 0
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
for name, address in ABSENT.items():
    documents[name] = read_string(address)
    declared = sorted(set(re.findall(r'\$(\w+)\s*:', documents[name])))
    print('%-16s %5d chars  declares %s' % (name, len(documents[name]), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
for name, text in documents.items():
    docs['last_' + name] = text
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'SignInAsGuestDocument' in text:
    raise SystemExit('already present')

anchor_line = [line for line in text.splitlines()
               if line.strip().startswith('/// <summary>maintainShippingGroups')]
if len(anchor_line) != 1:
    anchor_line = [line for line in text.splitlines()
                   if line.strip().startswith('/// <summary>createCartByStore')]
if len(anchor_line) != 1:
    raise SystemExit('no usable anchor')

blocks = []
rows = []
cases = []
for name, document in documents.items():
    declared = sorted(set(re.findall(r'\$(\w+)\s*:', document)))
    blocks.append('''    /// <summary>%s, %d characters from %#x.</summary>
    public const string %sDocument = "%s";
''' % (name, len(document), ABSENT[name], name, escape_literal(document)))
    rows.append('        ["%s"] = %s,' % (
        name,
        'new[] { ' + ', '.join('"%s"' % n for n in declared) + ' }' if declared else 'Array.Empty<string>()'))
    cases.append('        "%s" => %sDocument,' % (name, name))

text = text.replace(anchor_line[0], '\n'.join(blocks) + '\n' + anchor_line[0], 1)

row_anchor = '        ["createCartByStore"] ='
position = text.find(row_anchor)
end_of_row = text.find('\n', position)
text = text[:end_of_row] + '\n' + '\n'.join(rows) + text[end_of_row:]

switch_anchor = '        "createCartByStore" => CreateCartByStoreDocument,'
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor matched %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor + '\n' + '\n'.join(cases))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('three operations added to the session family')
