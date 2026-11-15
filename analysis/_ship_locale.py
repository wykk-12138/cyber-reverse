import io
p = r'D:\projects\cyber-reverse\replica\tools\locale-audit.py'
raw = io.open(p, 'rb').read().replace(b'\xef\xbb\xbf', b'')
head = '''"""Compare the image's key-shaped strings with the replica's locale keys.

Only keys under the replica's OWN top-level groups are considered, so library namespaces
(Acornima.Properties.*) and file names (ADVAPI32.dll) do not count as missing UI text.
The residue is classified as truncation / group-name / rename / noise.

R291 result: 1006 keys in scope, 21 absent, 0 real gaps.
"""
'''
io.open(p, 'wb').write(head.encode('utf-8') + raw)
print('locale-audit.py shipped')
