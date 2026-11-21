"""Does the replica already know the six `graphql?<Operation>` URLs the image lists?

The image keeps them in one alphabetised block:
https://www.paypal.com/graphql?ApproveOnboardPaymentMutation, ...?GetThreeDsJwtQuery,
...?OnboardGuestMutation, ...?ResolveThreeDsContingency, ...?ThreeDsAuthenticateMutation,
...?ThreeDsLookUpMutation
(there is no `graphql/partner` form anywhere in the inventory sample.)

If the replica composes these already, nothing to add; if it does not, the table is observed evidence that can
be dropped in without invention.

Usage: python analysis/check_gql_urls.py
"""
import io
import os

NEEDLES = [
    'graphql?',
    'paypal.com/graphql',
    'GetThreeDsJwtQuery',
    'ApproveOnboardPaymentMutation',
    'OnboardGuestMutation',
]

root = 'replica/src'
for needle in NEEDLES:
    hits = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if not name.endswith('.cs'):
                continue
            path = os.path.join(base, name)
            text = io.open(path, encoding='utf-8', errors='replace').read()
            count = text.count(needle)
            if count:
                hits.append('%s x%d' % (os.path.relpath(path, root), count))
    print('%-32s %s' % (needle, ', '.join(hits) or 'absent'))

text = io.open('replica/src/Cybersole.Stores/Payments/PayPalThreeDs.cs', encoding='utf-8').read()
index = text.find('EntryUrlFor')
if index >= 0:
    print()
    print('EntryUrlFor context:')
    print(text[max(0, index - 300):index + 500])
