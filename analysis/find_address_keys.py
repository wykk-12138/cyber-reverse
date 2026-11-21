"""What does the image call the fields of an AddressInput?

OnboardGuestMutation declares `$billingAddress: AddressInput` and the replica cannot build one without knowing
the field names. They are not in the document — GraphQL variables get their shape from the server's schema —
so the question is whether the image builds address objects anywhere in code, and if so with which keys.

This lists the candidate key names by exact match on the string's whole text, which is what a dictionary key or
an anonymous-object property name looks like in the pool.

Usage: python analysis/find_address_keys.py
"""
import io

CANDIDATES = (
    'line1', 'line2', 'line3', 'postalCode', 'postal_code', 'countryCode', 'country_code',
    'addressLine1', 'addressLine2', 'addressLines', 'adminArea', 'adminArea1', 'adminArea2',
    'streetNumber', 'streetName', 'street', 'givenName', 'familyName', 'phoneNumber',
    'fullName', 'address', 'city', 'state', 'zip', 'country', 'phone', 'email',
    'billingAddress', 'shippingAddress', 'firstname', 'lastname',
)

rows = []
for line in io.open('analysis/ida_strings.txt', encoding='utf-8', errors='replace'):
    if '\t' not in line:
        continue
    address, text = line.split('\t', 1)
    rows.append((address, text.rstrip()))

for key in CANDIDATES:
    hits = [(a, t) for a, t in rows if t.strip().strip('"') == key]
    if not hits:
        continue
    print('%-18s %2d hit(s)   first 0x%s  %r' % (key, len(hits), hits[0][0], hits[0][1][:40]))
