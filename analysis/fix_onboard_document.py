"""R1326: repair the Warhammer onboarding document that was pasted from a truncated display.

WarhammerQueries.g.cs ends its ApproveOnboardPaymentMutation constant with the literal marker
"[4040 chars total]" — a truncation notice from whatever printed the document during an earlier round. The
constant is 4022 characters and stops mid-document, so the flow has been sending a malformed GraphQL document
to the approval endpoint ever since.

The image's own copy is 4040 characters at 0x1470CC8CC and is what this writes back, byte for byte. The whole
tree was scanned for the same paste first (analysis/find_pasted_truncation.py) and this is the only instance.

Usage: python analysis/fix_onboard_document.py
"""
import io
import json

PATH = 'replica/src/Cybersole.Stores/Flows/WarhammerQueries.g.cs'
DOCS = 'analysis/.paypal_onboard.json'

text = io.open(PATH, encoding='utf-8', newline='').read()
document = json.loads(io.open(DOCS, encoding='utf-8').read())['approve_onboard_payment']

if 'chars total' not in text:
    raise SystemExit('the marker is gone already; nothing to repair')

start = text.index('    public const string ApproveOnboardPaymentMutation')
end = text.index('";', text.index('@"', start)) + 2
old = text[start:end]

literal = document.replace('"', '""')
new = (
    '    /// <summary>\n'
    '    /// R1326: rebuilt from the image (0x1470CC8CC, 4040 characters). The copy that was here ended with a\n'
    '    /// truncation marker pasted out of a display, so it stopped mid-document.\n'
    '    /// </summary>\n'
    '    public const string ApproveOnboardPaymentMutation = @"' + literal + '";'
)

text = text[:start] + new + text[end:]
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('replaced the constant: %d chars -> %d chars' % (len(old), len(new)))
