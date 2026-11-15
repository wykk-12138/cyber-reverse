import io
p = r'D:\projects\cyber-reverse\replica\tools\row_groups.py'
raw = io.open(p, 'rb').read().replace(b'\xef\xbb\xbf', b'')
io.open(p, 'wb').write(raw)
print('row_groups.py shipped', len(raw))
