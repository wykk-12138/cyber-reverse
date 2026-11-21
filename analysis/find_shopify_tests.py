"""R1331 tests: the structured cart-line edit, and the fallback that stays."""

import io

PATH = 'replica/tests/Cybersole.Tests/ShopifyGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read() if False else None

# Find the Shopify test file that already exercises the flow.
import os

candidates = [name for name in os.listdir('replica/tests/Cybersole.Tests') if 'Shopify' in name]
print('shopify test files: %s' % candidates)
