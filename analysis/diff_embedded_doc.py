"""Why is the embedded constant shorter than the decoded document?"""

import io
import json
import re

documents = json.loads(io.open('analysis/.highsnobiety_docs.json', encoding='utf-8').read())
document = documents['add_line_item']
print('decoded document: %d chars, %d quotes' % (len(document), document.count('"')))

source = io.open('replica/src/Cybersole.Stores/Flows/RetailFlows.cs', encoding='utf-8').read()
match = re.search(r'AddLineItemDocument = @"(.*?)";\n', source, re.S)
raw = match.group(1)
print('embedded raw:     %d chars, %d doubled pairs' % (len(raw), raw.count('""')))
print('embedded after un-doubling: %d' % len(raw.replace('""', '"')))

# Where do they first diverge? Compare the un-doubled text with the document.
un = raw.replace('""', '"')
for index in range(min(len(un), len(document))):
    if un[index] != document[index]:
        print('first difference at %d' % index)
        print('  embedded: %r' % un[max(0, index - 60):index + 60])
        print('  document: %r' % document[max(0, index - 60):index + 60])
        break
else:
    print('no difference in the common prefix; embedded ends at %d' % len(un))
    print('  document tail: %r' % document[len(un) - 40:len(un) + 80])
