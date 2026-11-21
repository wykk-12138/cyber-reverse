"""What variables does addLineItem actually declare and use?"""

import io
import json
import re

document = json.loads(io.open('analysis/.highsnobiety_docs.json', encoding='utf-8').read())['add_line_item']

declared = sorted(set(re.findall(r'\$(\w+)\s*:', document)))
used = sorted(set(re.findall(r'\$(\w+)', document)))

print('declared: %s' % declared)
print('used:     %s' % used)
print('mentions sku: %s' % ('sku' in document))

index = document.find('addLineItem(')
print('operation: %s' % document[index:index + 260].replace('\r', '').replace('\n', ' | '))

# Every fragment header, so the shape is visible.
for match in re.finditer(r'fragment (\w+) on (\w+)', document):
    print('fragment %s on %s' % (match.group(1), match.group(2)))
