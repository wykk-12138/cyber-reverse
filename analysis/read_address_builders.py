"""What do the two functions that reference recipientName carry in their literal tables?"""

import io
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

for label, path in (('0x140AD5B10', r'C:\Users\wykk\AppData\Local\Temp\r1378_a.c'),
                    ('0x140F4BA90', r'C:\Users\wykk\AppData\Local\Temp\r1378_b.c')):
    code = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
    decoded = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                             capture_output=True, text=True).stdout
    strings = [line.split("'", 2)[1] for line in decoded.splitlines()
               if ' str ' in line and "'" in line]

    print('=== %s  %d literals' % (label, len(strings)))
    print('    %s' % ' | '.join(s[:30] for s in strings[:22]))
    address_words = [s for s in strings
                     if s.lower() in ('addressline1', 'addressline2', 'locality', 'postalcode', 'recipientname',
                                      'countrycode', 'phonenumber', 'firstname', 'lastname', 'city', 'street',
                                      'postcode', 'country_id', 'telephone', 'address')]
    print('    address-shaped literals: %s' % (address_words or 'none'))
    print()
