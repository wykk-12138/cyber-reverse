"""R1284: classify BstnFlow's four placeholders instead of leaving them as "unknown".

What the evidence says, and what each line has to stop claiming:
  * /api/beast            live-proven (geoIP and monetate answered) but no literal in the image -> "route unrecorded"
  * /cart.js              404 on the store                                        -> "route absent at the store"
  * Adyen checkout        live host checkoutanalytics-live.adyen.com, no order route recorded -> "order route unrecorded"
  * product endpoint      page-driven, no literal anywhere                        -> "page-driven, unattested"

The wording change matters: "unknown" reads as "nobody looked", and every one of these was looked at.
"""

import io

P = 'src/Cybersole.Stores/Flows/BstnFlow.cs'
text = io.open(P, encoding='utf-8').read()

subs = [
    # the header's counting line
    ("/// Unknown:    the product endpoint, the cart endpoint, the checkout endpoint",
     "/// Unrecorded: the product endpoint (page-driven), the cart route, the Adyen order route — each classified\n"
     "/// below with what was checked, per docs/ENDPOINT_PROVENANCE.md ('live' = answered, no image literal)."),

    # add-to-cart: live-proven prefix, unrecorded child route
    ('"bstn: cart endpoint unknown — /cart.js is 404 and the cart lives under /api/beast/ " +',
     '"bstn: cart route unrecorded — /cart.js answers 404 and /api/beast is live-proven only for " +\n'
     '        "geoIP and monetate, so the add route is not attested " +'),

    # cart
    ('Task.FromResult(StepOutcome.Fail("bstn: cart endpoint unknown"));',
     'Task.FromResult(StepOutcome.Fail(\n'
     '            "bstn: cart route unrecorded — /api/beast answers, its cart child route does not appear anywhere"));'),

    # checkout
    ('Task.FromResult(StepOutcome.Fail("bstn: checkout endpoint unknown (Adyen)"));',
     'Task.FromResult(StepOutcome.Fail(\n'
     '            "bstn: checkout is live on checkoutanalytics-live.adyen.com; no checkout route is recorded"));'),

    # order
    ('Task.FromResult(StepOutcome.Fail("bstn: order endpoint unknown"));',
     'Task.FromResult(StepOutcome.Fail(\n'
     '            "bstn: order route unrecorded — Adyen answers, the submit path is not attested anywhere"));'),
]

for old, new in subs:
    if old not in text:
        print('MISS:', old[:70])
        continue
    text = text.replace(old, new)
    print('ok  :', old[:70])

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('unknown left:', text.count('endpoint unknown'))
