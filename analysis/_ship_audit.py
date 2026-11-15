import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-audit.py'
raw = io.open(p, 'rb').read().replace(b'\xef\xbb\xbf', b'')
head = '''"""Static audit of mutation-check's anchors: no tests are run.

Every mutation locates its defect with a `find` string. When that string drifts — a comment gets reworded, a number in a
doc gets updated — the tool skips the mutation SILENTLY and still counts it in "24 guards". A guard that never runs is
worse than no guard, because it still appears in the report.

Run after any change to the files the mutations touch:
    <python> tools/mutation-audit.py
"""

'''
io.open(p, 'wb').write(head.encode('utf-8') + raw)
print('mutation-audit.py shipped')
