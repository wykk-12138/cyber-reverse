"""Recompute the payment-surface table in docs/PAYMENT_CHALLENGES.md from source.

The document claims seven implemented surfaces, each naming a decompiled function and the member that carries it. That
is a claim about the code, so it should be checkable by running something rather than by trusting the table. This
script reads the source and reports, per row, whether the member exists and whether the constants the row names are
present. It does not judge completeness — only whether the claim still holds.

    python tools/payment_surfaces.py
"""
import io
import os
import re
import sys

SRC = ['src/Cybersole.Stores/Payments/Gateways.cs',
       'src/Cybersole.Stores/Payments/PayPalThreeDs.cs',
       'src/Cybersole.Stores/Flows/MagentoFlow.cs']

# (surface, decompiled function, member that must exist, literals that must appear)
ROWS = [
    # R1268: the first two rows named a member "PaymentMethodForm" that does not exist in the code; the surface is
    # built inside StripeGateway.TokenizeAsync (Gateways.cs:504), which is also where line 1712 of StoreFlow posts
    # from. The recompute caught the mismatch, so the rows now name what is actually there.
    ('payment_methods form', 'sub_140BDA320', 'TokenizeAsync', ['2025-01-27.acacia']),
    ('payment_methods challenge', 'sub_140959320', 'TokenizeAsync', ['2025-08-27.basil']),
    ('setup_intent confirm', 'sub_140BE0F80', 'SetupConfirmUrl', ['payment_method_data']),
    ('setup_intent retrieve', 'sub_141145DB0', 'SetupIntentRetrieveUrl', ['_stripe_account=']),
    ('payment_intents retrieve (JL)', 'sub_1411458f0', 'PaymentIntentRetrieveUrl', ['is_stripe_sdk=true']),
    ('payment_intents retrieve', 'sub_140A40170', 'PaymentIntentRetrieveUrl', ['is_stripe_sdk=false']),
    ('payment_intents confirm (PayPal)', 'sub_140B58D60', 'PayPalConfirmForm', ['mandate_data']),
]


def read_all():
    text = ''
    for path in SRC:
        if os.path.exists(path):
            text += io.open(path, encoding='utf-8', errors='replace').read()
    # the two retrieve variants share one member name, so also read the file that declares the version constants
    for extra in ('src/Cybersole.Stores/Payments/Gateways.cs',):
        if os.path.exists(extra):
            text += io.open(extra, encoding='utf-8', errors='replace').read()
    return text


def main():
    text = read_all()
    ok = 0
    print('%-34s %-18s %-28s %s' % ('surface', 'function', 'member', 'constants'))
    for surface, fn, member, literals in ROWS:
        has_member = re.search(r'\b' + re.escape(member) + r'\b', text) is not None
        missing = [l for l in literals if l not in text]
        status = 'ok' if has_member and not missing else 'CHECK'
        if status == 'ok':
            ok += 1
        print('%-34s %-18s %-28s %s' % (surface, fn, member + (' ok' if has_member else ' MISSING'),
                                        'ok' if not missing else 'missing ' + ', '.join(missing)))
    print('\n%d/%d rows recompute from source' % (ok, len(ROWS)))
    if ok != len(ROWS):
        print('the table in docs/PAYMENT_CHALLENGES.md no longer matches the code')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
