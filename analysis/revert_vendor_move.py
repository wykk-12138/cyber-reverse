"""Put the four test files back on VendorWiring after the move was reverted (R1281)."""
import io

FILES = [
    'tests/Cybersole.Tests/VendorWiringTests.cs',
    'tests/Cybersole.Tests/WallDispatchTests.cs',
    'tests/Cybersole.Tests/WallSolvingTests.cs',
    'tests/Cybersole.Tests/CaptchaDeliveryAttributionTests.cs',
]

for path in FILES:
    text = io.open(path, encoding='utf-8').read()
    text = text.replace('VendorAuditTable', 'VendorWiring')
    text = text.replace('"tests", "Cybersole.Tests", "VendorWiring.cs"',
                        '"src", "Cybersole.Stores", "Scripts", "VendorWiring.cs"')
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    print(path, 'reverted')
