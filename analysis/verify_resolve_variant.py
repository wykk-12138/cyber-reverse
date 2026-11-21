"""Check that the new variant constant is byte-identical to the image's document, and list its callers."""

import io
import re

SOURCE = 'replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs'
text = io.open(SOURCE, encoding='utf-8').read()

match = re.search(r'ResolveDocumentWithoutProviderFields\s*=\s*@"(.*?)";', text, re.S)
if not match:
    raise SystemExit('variant constant not found')

variant = match.group(1).replace('""', '"')
image = io.open('analysis/.three_ds_a.txt', encoding='utf-8').read()

print('variant in source: %d chars' % len(variant))
print('image variant A:   %d chars' % len(image))
print('identical: %s' % (variant == image))
print('contains the provider block: %s' % ('authenticationProvider' in variant))
print('selector mentions the flag: %s' % ('providerFields ? ResolveDocument' in text))

# Which files call DocumentFor, so the reader can see the default is what they get.
import os
callers = []
for root, dirs, files in os.walk('replica'):
    dirs[:] = [d for d in dirs if d not in ('bin', 'obj', '.publish-aot', '.publish-aot-prev', '.publish-aot-new')]
    for name in files:
        if not name.endswith('.cs'):
            continue
        path = os.path.join(root, name)
        body = io.open(path, encoding='utf-8', errors='replace').read()
        if 'DocumentFor(' in body and path.replace('\\', '/') != SOURCE:
            callers.append(path)
print('callers: %s' % (callers or 'none outside the class'))
