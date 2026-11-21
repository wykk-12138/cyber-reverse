"""What does the Warhammer flow already keep in the session? The onboarding hop needs to reuse it."""

import io
import re

text = io.open('replica/src/Cybersole.Stores/Flows/RetailFlows.cs', encoding='utf-8').read()
start = text.index('class WarhammerFlow')
end = text.find('\npublic sealed class ', start + 10)
segment = text[start:end if end > 0 else len(text)]

keys = sorted({m.group(1) for m in re.finditer(r'Vars\["([^"]+)"\]', segment)})
print('session keys the Warhammer flow writes or reads:')
for key in keys:
    print('  %s' % key)

print()
print('billing address construction present: %s' % ('billingAddress' in segment))
print('shipping address construction present: %s' % ('shippingAddress' in segment))
