"""Is the shipped Warhammer copy of ApproveOnboardPaymentMutation the image's document?

The flow sends WarhammerQueries.ApproveOnboardPaymentMutation as an operationName-plus-query pair, and the
image holds a document of the same name at 0x1470CC8CC. If the two differ, the replica is sending a document
the store may not accept, which would be a fidelity bug rather than a missing feature — worth knowing either
way, and cheap to check.

Usage: python analysis/compare_onboard.py
"""
import io
import json
import re

docs = json.loads(io.open('analysis/.paypal_onboard.json', encoding='utf-8').read())
image = docs['approve_onboard_payment']

text = io.open('replica/src/Cybersole.Stores/Flows/WarhammerQueries.g.cs', encoding='utf-8').read()
match = re.search(r'ApproveOnboardPaymentMutation\s*=\s*@"(.*?)";', text, re.S)
if not match:
    raise SystemExit('constant not found in WarhammerQueries.g.cs')

replica = match.group(1).replace('""', '"')

print('image:   %d chars' % len(image))
print('replica: %d chars' % len(replica))
print('identical: %s' % (replica == image))
print()
if replica != image:
    import difflib
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, replica, image, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        print('%-8s replica[%d:%d] %s' % (tag, i1, i2, replica[i1:i2][:120].replace('\n', '\\n')))
        print('%-8s image  [%d:%d] %s' % ('', j1, j2, image[j1:j2][:120].replace('\n', '\\n')))
