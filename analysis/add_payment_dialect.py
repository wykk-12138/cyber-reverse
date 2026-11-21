"""R1370: the two approveMemberPayment dialects differ by exactly one variable, and that is the condition.

Comparing the declared sets settles four rounds of "which dialect, and when":

    short (5407) declares 15 — ..., selectedInstallmentOption, setStickyFiRequired, shareAddressWithDonatee, token
    long  (5620) declares 16 — the same plus paycodeEncrypted

Nothing else differs. So the dialect follows the payment, not the store: a funding option that carries an encrypted
paycode needs the long document, and everything else takes the short one. That is a condition the caller can decide
from its own payload, which is where it belongs — the image gives no store list, and inventing one would be a guess.

This adds the long document to PayPalPartnerApprove and a DocumentFor(paycodeEncrypted) selector, and keeps the
existing Document constant pointing at the short one so nothing that already uses it changes.

Usage: python analysis/add_payment_dialect.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

LONG_SOURCE = 0x1470EC9FC
PATH = 'replica/src/Cybersole.Stores/Payments/PayPalPartnerApprove.cs'


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


def dotnet_verbatim(text):
    return text.replace('"', '""')


long_document = read_string(LONG_SOURCE)
long_declared = sorted(set(re.findall(r'\$(\w+)\s*:', long_document)))
print('long dialect: %d chars  declares %d variables' % (len(long_document), len(long_declared)))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'PaycodeDocument' in text:
    raise SystemExit('already present')

anchor = '    public static readonly string[] VariableNames ='
if text.count(anchor) != 1:
    raise SystemExit('anchor matched %d times' % text.count(anchor))

block = '''    /// <summary>
    /// The same mutation with one more declared variable: <c>paycodeEncrypted</c>. 5620 characters from 0x1470EC9FC,
    /// against the 5407-character document above. The declared sets are identical apart from that name, which is the
    /// whole of the difference — so the dialect follows the funding option, not the store.
    /// </summary>
    public const string PaycodeDocument = @"%s";

    /// <summary>The variable that decides between the two dialects.</summary>
    public const string PaycodeVariableName = "paycodeEncrypted";

    /// <summary>
    /// The document a payment needs. A funding option carrying an encrypted paycode declares it, and only then is the
    /// longer document the right one; everything else takes the document this class has always sent.
    /// </summary>
    public static string DocumentFor(bool carriesPaycode) => carriesPaycode ? PaycodeDocument : Document;

    /// <summary>The envelope for whichever dialect the payment needs.</summary>
    public static JObject EnvelopeFor(JObject variables)
    {
        var carriesPaycode = variables?[PaycodeVariableName] is not null;
        return new JObject
        {
            ["operationName"] = OperationName,
            ["query"] = DocumentFor(carriesPaycode),
            ["variables"] = variables ?? new JObject(),
        };
    }

''' % dotnet_verbatim(long_document)

text = text.replace(anchor, block + anchor, 1)
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('long dialect and selector added to PayPalPartnerApprove')
