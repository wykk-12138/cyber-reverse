"""Print the raw string-pool lines at descriptor addresses (context for the gap investigation)."""
import io
import re

addresses = {
    '0x0322278f', '0x03216368', '0x03215e33', '0x03217175', '0x0321d914',
    '0x0321dab0', '0x032215e9', '0x0321d6ce', '0x032154a7', '0x03216cf9',
    '0x03210b67', '0x03210a9b', '0x032103cd', '0x03210162', '0x0321061a',
    '0x0321176a', '0x0321274d', '0x032143af', '0x0321d536', '0x0321b11e',
}

pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
for line in io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines():
    m = pat.match(line)
    if not m:
        continue
    addr, text = m.group(1), m.group(2)
    if addr in addresses:
        print('==', addr, 'len', len(text))
        print(text[:1000])
        print()
