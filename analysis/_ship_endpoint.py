import io
p = r'D:\projects\cyber-reverse\replica\tools\endpoint-ledger.py'
raw = io.open(p, 'rb').read().replace(b'\xef\xbb\xbf', b'')
head = '''"""Classify the replica's API paths by how well the image's string pool backs them.

Three buckets: verbatim (whole path present), composed (last one or two segments present) and no evidence.
R293 result: 89 paths = 44 verbatim + 23 composed + 22 unbacked. The unbacked list lives in
tests/Cybersole.Tests/EndpointEvidenceRatchetTests.cs so it can only shrink.
"""
'''
io.open(p, 'wb').write(head.encode('utf-8') + raw)
print('endpoint-ledger.py shipped')
