"""Point the four remaining test files at VendorAuditTable (R1281).

Written as a file rather than an inline command because the quoting needs both kinds of quotes.
"""
import io

FILES = [
    'tests/Cybersole.Tests/VendorWiringTests.cs',
    'tests/Cybersole.Tests/WallDispatchTests.cs',
    'tests/Cybersole.Tests/WallSolvingTests.cs',
    'tests/Cybersole.Tests/CaptchaDeliveryAttributionTests.cs',
]

for path in FILES:
    text = io.open(path, encoding='utf-8').read()
    text = text.replace('Cybersole.Stores.Scripts.VendorWiring', 'VendorAuditTable')
    text = text.replace('VendorWiring.', 'VendorAuditTable.')
    text = text.replace('"VendorWiring.cs"', '"VendorAuditTable.cs"')
    # the file no longer lives under src; the path literal in the attribution test has to follow it
    text = text.replace('"src", "Cybersole.Stores", "Scripts", "VendorAuditTable.cs"',
                        '"tests", "Cybersole.Tests", "VendorAuditTable.cs"')
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    print(path, 'ok')
