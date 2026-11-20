"""Close the two methods whose body was cut, replacing the dangling call with the method's brace (R1282)."""
import io

FIXES = [
    ('tests/Cybersole.Tests/VendorNegativeClaimsTests.cs',
     'var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),'),
    ('tests/Cybersole.Tests/CaptchaDeliveryAttributionTests.cs',
     'var audit = File.ReadAllText(Path.Combine(RepoRoot(),'),
]

for path, marker in FIXES:
    lines = io.open(path, encoding='utf-8').read().split('\n')
    idx = next((i for i, l in enumerate(lines) if marker in l), None)
    if idx is None:
        print('marker missing in', path)
        continue
    lines[idx:idx + 1] = ['    }']
    io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print('closed method in', path)
