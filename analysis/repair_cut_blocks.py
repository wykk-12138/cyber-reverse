"""Repair the two blocks the previous pass cut mid-statement (R1282)."""
import io

FIXES = [
    ('tests/Cybersole.Tests/VendorNegativeClaimsTests.cs',
     'var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),'),
    ('tests/Cybersole.Tests/CaptchaDeliveryAttributionTests.cs',
     'var audit = File.ReadAllText(Path.Combine(RepoRoot(),'),
]

for path, marker in FIXES:
    lines = io.open(path, encoding='utf-8').read().split('\n')
    start = next((i for i, l in enumerate(lines) if marker in l), None)
    if start is None:
        print('marker missing in', path)
        continue
    # the dangling block runs until the first Assert statement that ends the sequence
    end = None
    for i in range(start, min(start + 8, len(lines))):
        if lines[i].lstrip().startswith('Assert') and lines[i].rstrip().endswith(';'):
            end = i
            break
    if end is None:
        # no Assert left: the block is just the dangling call, close on the line ending with '));'
        for i in range(start, min(start + 4, len(lines))):
            if lines[i].rstrip().endswith('));'):
                end = i
                break
    if end is None:
        print('cannot find block end in', path)
        continue
    del lines[start:end + 1]
    io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print('repaired %s (%d lines removed)' % (path, end - start + 1))
