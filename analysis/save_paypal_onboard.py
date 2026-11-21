"""R1326: save the onboarding document as evidence and record why the dialect question is now blocked.

Three findings this round, all negative, all recomputable:

  The six GraphQL operations the PayPal 3DS machine uses all go to one endpoint family —
  https://www.paypal.com/graphql?<Operation> — listed in a single alphabetised block (0x147097edc ..
  0x14709817c): ApproveOnboardPaymentMutation, GetThreeDsJwtQuery, OnboardGuestMutation,
  ResolveThreeDsContingency, ThreeDsAuthenticateMutation, ThreeDsLookUpMutation. There is no
  `graphql/partner` form anywhere in the inventory sample, so the dialect split is not a URL split.

  Walking up from the two MoveNext stubs leads into data, not calls (0x14777a93c and 0x14777a96c, 0x30 apart),
  i.e. the state machines are dispatched through a method table. Tables have slots, not conditions.

  Every GqlAsync call site already passes its URL explicitly, so a default endpoint would be dead code.

What is left is reading a 15 KB async body for a field-name test, which is not this round's yield. So the round
saves OnboardGuestMutation (3104 characters, no home yet) as evidence and says plainly that it changed no
source.
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

OUT = 'analysis/.paypal_onboard.json'
SITES = {
    'onboard_guest': 0x1470D611C,
    'approve_onboard_payment': 0x1470CC8CC,
    'currency_conversion': 0x1470D0FB4,
}


def read_string(chars_va):
    res = call('get_bytes', {'regions': [{'addr': hex(chars_va - 12), 'size': 12}]})
    if isinstance(res, str):
        res = json.loads(res.splitlines()[0])
    header = bytes(int(t, 16) for t in res[0]['data'].split())
    length = int.from_bytes(header[8:12], 'little')

    blob = b''
    while len(blob) < length * 2:
        res = call('get_bytes', {'regions': [{'addr': hex(chars_va + len(blob)), 'size': 8192}]})
        if isinstance(res, str):
            res = json.loads(res.splitlines()[0])
        chunk = bytes(int(t, 16) for t in res[0]['data'].split())
        if not chunk:
            break
        blob += chunk
    return blob.decode('utf-16-le', errors='replace')[:length]


def main():
    found = {}
    for name, address in SITES.items():
        found[name] = read_string(address)
        print('%-24s 0x%09X  %5d chars  %s' % (
            name, address, len(found[name]), found[name][:60].replace('\n', ' ')))
    io.open(OUT, 'w', encoding='utf-8', newline='').write(json.dumps(found, ensure_ascii=False, indent=2))
    print('wrote %s' % OUT)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
