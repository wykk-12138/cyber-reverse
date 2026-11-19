"""Extract the VendorWiring row table for the docs migration (R1274)."""
import io
import re

SRC = 'src/Cybersole.Stores/Scripts/VendorWiring.cs'
text = io.open(SRC, encoding='utf-8').read()

print('== rows (vendor, marker, cookie, state)')
for m in re.finditer(r'new Row\("([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*State\.(\w+)', text):
    print('%-12s | %-22s | %-20s | %s' % m.groups())

print('\n== enums')
for m in re.finditer(r'public enum (\w+)\s*\{(.*?)\n    \}', text, re.S):
    body = [x.strip().rstrip(',') for x in m.group(2).split('\n')
            if x.strip() and not x.strip().startswith('//') and not x.strip().startswith('///')]
    print('%s: %s' % (m.group(1), ' · '.join(body)))

print('\n== Row record')
for m in re.finditer(r'public sealed record Row\((.*?)\);', text, re.S):
    print(' '.join(m.group(1).split()))
