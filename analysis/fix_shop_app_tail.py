"""Fix the tail assertion with the measured text rather than an escaped guess."""

import io
import json

DOCS = 'analysis/.shop_app_docs.json'
TESTS = 'replica/tests/Cybersole.Tests/ShopAppProductTests.cs'

document = json.loads(io.open(DOCS, encoding='utf-8').read())['product_details']
tail = document[-24:]
print('measured tail: %r' % tail)

escaped = (tail.replace('\\', '\\\\').replace('"', '\\"')
               .replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t'))

text = io.open(TESTS, encoding='utf-8').read()
start = text.find('        Assert.EndsWith(')
if start < 0:
    raise SystemExit('tail assertion not found')
end = text.find('\n', start)

replacement = ('        // The document ends in a closing brace, a CRLF and trailing spaces — measured, not assumed.\n'
               '        Assert.EndsWith("%s", ShopAppProduct.Document);' % escaped)
text = text[:start] + replacement + text[end:]
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('assertion rewritten')
