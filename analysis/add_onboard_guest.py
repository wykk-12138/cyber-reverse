"""R1328: land OnboardGuestMutation in WarhammerQueries and wire the onboarding hop before approval.

Why this belongs in the Warhammer flow rather than nowhere: the document's variables are exactly the things
that flow already collects — billingAddress and shippingAddress from its two address steps, email/firstName/
lastName/phone from the profile, card from the card step, and `token` from the provider. Its sibling,
ApproveOnboardPaymentMutation, is already sent by that flow to ApiHost + "/graphql", and the two are adjacent
in the image's own URL table (graphql?OnboardGuestMutation sits between ?GetThreeDsJwtQuery and
?OnboardGuestMutation's neighbours at 0x147097fe4).

Ordering (onboard, then approve) is an Inference, and it is recorded as one: onboarding produces the buyer that
approval's reply refers to, but no literal in the image shows the sequence.

The document is written from the decoded bytes, never pasted — R1326's lesson.

Usage: python analysis/add_onboard_guest.py
"""
import io
import json

QUERIES = 'replica/src/Cybersole.Stores/Flows/WarhammerQueries.g.cs'
DOCS = 'analysis/.paypal_onboard.json'

text = io.open(QUERIES, encoding='utf-8', newline='').read()
if 'OnboardGuestMutation' in text:
    raise SystemExit('document already present')

document = json.loads(io.open(DOCS, encoding='utf-8').read())['onboard_guest']
literal = document.replace('"', '""')

block = (
    '\n'
    '    /// <summary>\n'
    '    /// R1328: the guest-onboarding mutation, 3104 characters from 0x1470D611C. It is the step before\n'
    '    /// <see cref="ApproveOnboardPaymentMutation"/> — it takes the same addresses, the card and the\n'
    '    /// provider token the approval takes, and produces the buyer the approval refers to.\n'
    '    /// </summary>\n'
    '    public const string OnboardGuestMutation = @"' + literal + '";\n'
)

# Put it next to its sibling so the pair reads as a pair.
anchor = '    public const string ApproveOnboardPaymentMutation'
index = text.index(anchor)
# Back up over the sibling's doc comment so the new block lands above it.
line_start = text.rindex('\n\n', 0, index) + 2
text = text[:line_start] + block.lstrip('\n') + '\n' + text[line_start:]

io.open(QUERIES, 'w', encoding='utf-8', newline='').write(text)
print('added OnboardGuestMutation (%d chars) to WarhammerQueries' % len(document))
