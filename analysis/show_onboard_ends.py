"""Print the head and tail of both onboarding documents so the difference is visible."""

import io
import json
import re

docs = json.loads(io.open('analysis/.paypal_onboard.json', encoding='utf-8').read())
image = docs['approve_onboard_payment']

text = io.open('replica/src/Cybersole.Stores/Flows/WarhammerQueries.g.cs', encoding='utf-8').read()
match = re.search(r'ApproveOnboardPaymentMutation\s*=\s*@"(.*?)";', text, re.S)
replica = match.group(1).replace('""', '"')

print('image   %d chars' % len(image))
print('replica %d chars' % len(replica))
print()
print('image  head: %s' % image[:110].replace('\n', '\\n'))
print('replica head: %s' % replica[:110].replace('\n', '\\n'))
print()
print('image  tail: %s' % image[-150:].replace('\n', '\\n'))
print('replica tail: %s' % replica[-150:].replace('\n', '\\n'))
print()
print('image contains "__typename": %s' % ('__typename' in image))
print('replica contains "__typename": %s' % ('__typename' in replica))
