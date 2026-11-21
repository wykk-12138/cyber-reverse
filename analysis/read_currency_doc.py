"""Read the CurrencyConversion document's declared variables."""

import io
import json
import re

docs = json.loads(io.open('analysis/.magento_cart_docs.json', encoding='utf-8').read())
text = docs['currency_conversion']

print('length: %d' % len(text))
print('head: %s' % text[:400].replace('\n', ' | '))
print()
variables = re.findall(r'\$(\w+)', text)
seen = []
for name in variables:
    if name not in seen:
        seen.append(name)
print('declared/referenced variables (%d): %s' % (len(seen), ', '.join(seen)))
