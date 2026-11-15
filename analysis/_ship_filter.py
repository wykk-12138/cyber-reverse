import io
p = r'D:\projects\cyber-reverse\replica\tools\flow_filter.py'
raw = io.open(p,'rb').read().replace(b'\xef\xbb\xbf', b'')
io.open(p,'wb').write(raw)
print('flow_filter.py shipped')
