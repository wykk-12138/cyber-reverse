"""R1343b: the class was trimmed. Reachability applies to the API surface, not just to documents.

After adding PayPalCheckoutQueries — 20650 bytes of source with two documents — the artifact size did not move at
all (61,630,976 both before and after) and neither document was findable in either encoding. That is the signature
of trimming: the documents are referenced by PayWithAsync and ShipToAsync, which satisfy the R1331 invariant, but
nothing calls those methods, so the whole class is unreachable and AOT drops it.

§4.5 says absence in the artifact proves nothing on its own; a completely unchanged size while adding twenty
kilobytes of source is the part that does mean something. Either way the fix is the same: give it a caller.

PayPalGateway.AuthorizeAsync already has leading branches for the partner approval and the currency conversion,
each keyed by a session value a capture supplies. The checkout query joins them.

Usage: python analysis/wire_checkout_queries.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Payments/Gateways.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'PayPalCheckoutQueries' in text:
    raise SystemExit('already wired')

anchor = '''        // R1336: the conversion goes first when the run asks for one.'''
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

branch = '''        // R1343: the checkout pair, when a run asks for it. PayWithQuery says what the buyer can pay with and
        // ShipToQuery where it ships; both are keyed by the buyer token and both go to the partner base, so they
        // run before the approval that uses their answers. Same reasoning as the conversion above: a session key
        // a capture supplies, no invented defaults.
        if (!string.IsNullOrEmpty(partnerToken) &&
            string.Equals(c.Session.Vars.GetValueOrDefault("paypal.checkout"), "true", StringComparison.OrdinalIgnoreCase))
        {
            var token = new JObject { ["token"] = partnerToken };

            var (payWith, payWithError) = await PayPalCheckoutQueries
                .PayWithAsync(c, new JObject
                {
                    ["token"] = partnerToken,
                    ["withSplitTender"] = false,
                    ["expeirences"] = new JArray(),
                }, ct, c.Session.Vars.GetValueOrDefault("paypal.payWithUrl")).ConfigureAwait(false);
            if (payWith is null) return PaymentResult.Fail(payWithError);
            c.Session.Vars["paypal.payWith"] = payWith.ToString(Newtonsoft.Json.Formatting.None);

            var (shipTo, shipToError) = await PayPalCheckoutQueries
                .ShipToAsync(c, token, ct, c.Session.Vars.GetValueOrDefault("paypal.shipToUrl"))
                .ConfigureAwait(false);
            if (shipTo is null) return PaymentResult.Fail(shipToError);
            c.Session.Vars["paypal.shipTo"] = shipTo.ToString(Newtonsoft.Json.Formatting.None);
        }

'''

text = text.replace(anchor, branch + anchor)
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('wired the checkout pair in front of the conversion')
