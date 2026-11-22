"""Point the three addresses at the values the inventory actually holds, then re-run."""

import io
import json

path = 'analysis/add_last_three_operations.py'
text = io.open(path, encoding='utf-8').read()

inventory = json.loads(io.open('analysis/.operations_in_image.json', encoding='utf-8').read())
correct = {name: int(inventory[name]['addr']) for name in ('SignInAsGuest', 'addToCart', 'buynow')}
print('inventory addresses: %s' % {k: hex(v) for k, v in correct.items()})

text = text.replace('0x1474A4D8C', hex(correct['addToCart']))
text = text.replace('0x1474A4F74', hex(correct['buynow']))
io.open(path, 'w', encoding='utf-8', newline='').write(text)
print('script updated')
