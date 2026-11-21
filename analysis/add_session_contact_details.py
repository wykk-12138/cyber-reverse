"""R1363: UpdateContactDetails joins the session family, and its twin sends by hash.

Two handlers again. sub_140891BB0 builds https:// + host + /graphql with email, emailOptIn and phone — the same
shape as the session family, where the origin is the caller's. sub_14088C0C0 sits in the block that sends persisted
queries by hash (R1357): a Sentry trace header, two more 64-hex values, "Submitting Email".

So the document joins StoreSessionQueries, whose origin is the caller's; a caller that needs the /graphql suffix
passes it as part of the origin, which the class documents. The hash twin is recorded and not implemented, because
which of the two a run picks is the same unanswered question as the two approveMemberPayment dialects.

Usage: python analysis/add_session_contact_details.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470E37BC
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
print('UpdateContactDetails: %d chars  declares %s' % (len(document), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['update_contact_details'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'UpdateContactDetails' in text:
    raise SystemExit('already present')

anchor_line = [line for line in text.splitlines()
               if line.strip().startswith('/// <summary>addToCartByChannel')]
if len(anchor_line) != 1:
    raise SystemExit('anchor line matched %d times' % len(anchor_line))

constants = '''    /// <summary>
    /// UpdateContactDetails, %d characters from 0x1470E37BC. Its other handler sends the same operation by hash
    /// from the 0x14088xxxx block (R1357); which one a run picks is not established, so only this one is wired.
    /// </summary>
    public const string UpdateContactDetailsDocument = "%s";

''' % (len(document), escape_literal(document))

text = text.replace(anchor_line[0], constants + anchor_line[0], 1)

declared_anchor = '["addToCartByChannel"] = new[] {'
if text.count(declared_anchor) != 1:
    raise SystemExit('declared row matched %d times' % text.count(declared_anchor))
row = '\n        ["UpdateContactDetails"] = new[] { %s },' % ', '.join('"%s"' % n for n in declared)
position = text.find(declared_anchor)
end_of_row = text.find('\n', position)
text = text[:end_of_row] + row + text[end_of_row:]

switch_anchor = '        "addToCartByChannel" => AddToCartByChannelDocument,'
if text.count(switch_anchor) != 1:
    raise SystemExit('switch anchor matched %d times' % text.count(switch_anchor))
text = text.replace(switch_anchor, switch_anchor + '\n        "UpdateContactDetails" => UpdateContactDetailsDocument,')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('UpdateContactDetails added to the session family')
