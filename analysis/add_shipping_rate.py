"""R1330: the flow extracted a shipping rate id and never sent it. Send it.

WarhammerQueries.UpdateShippingRate is 2248 characters of observed mutation —
`mutation ($selectedShippingRateId: Int, $isNewsletterSubscribed: Boolean) { updateShippingRate(...) { errors
order { number checkoutVersion state adyenTotalAmount guestToken isRegistrationValid isShippingValid
isPaymentValid ... } } }` — and nothing in src called it. Meanwhile SubmitShippingAsync reads a rate id out of
the address response at line 1030 and drops it on the floor.

So the step was half done: the address went out, the chosen rate never did, and the order would stay at the
"shipping invalid" state the mutation itself reports. This adds the second hop, guarded by the id actually
being there, and keeps the order block the mutation returns.

Usage: python analysis/add_shipping_rate.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'UpdateShippingRate' in text:
    raise SystemExit('rate hop already present')

old_tail = '''        c.Session.Vars["shipping"] = res.Body;
        var rate = Regex.Match(res.Body, @"""id""\\s*:\\s*(\\d+)");
        if (rate.Success) c.Session.Vars["shippingRateId"] = rate.Groups[1].Value;
        return StepOutcome.Success();
    }'''
if text.count(old_tail) != 1:
    raise SystemExit('shipping tail found %d times' % text.count(old_tail))

new_tail = '''        c.Session.Vars["shipping"] = res.Body;
        var rate = Regex.Match(res.Body, @"""id""\\s*:\\s*(\\d+)");
        if (!rate.Success || !int.TryParse(rate.Groups[1].Value, out var rateId))
        {
            // R1330: the address went out but no rate came back, so there is nothing to select. Say so instead
            // of returning success with the order still at isShippingValid=false.
            c.Emit("warhammer: the address reply carries no shipping rate id, so no rate was selected", "StatusInfo");
            return StepOutcome.Success();
        }

        c.Session.Vars["shippingRateId"] = rate.Groups[1].Value;

        // R1330: the observed UpdateShippingRate mutation (2248 characters, WarhammerQueries). Its variables are
        // the rate the address reply just offered and the newsletter flag, which this flow never sets, so false.
        var rateBody = new JObject
        {
            // anonymous in the image, like its sibling: no operationName travels with it
            ["query"] = WarhammerQueries.UpdateShippingRate,
            ["variables"] = new JObject
            {
                ["selectedShippingRateId"] = rateId,
                ["isNewsletterSubscribed"] = false,
            },
        };

        var rated = await PostJsonAsync(c, ApiHostFor(c) + "/graphql",
            rateBody.ToString(Newtonsoft.Json.Formatting.None), "wh-shipping-rate", ct).ConfigureAwait(false);

        if (rated is null) return StepOutcome.Fail("warhammer shipping rate failed", retryable: true);
        if (rated.IsSuccess && rated.Body.Contains("\\"errors\\"", StringComparison.Ordinal))
            return StepOutcome.Fail("warhammer shipping rate: graphql returned errors");
        if (!rated.IsSuccess)
            return StepOutcome.Fail($"warhammer shipping rate HTTP {rated.StatusCode}", retryable: true);

        c.Session.Vars["shippingRate"] = rated.Body;
        foreach (var key in new[] { "checkoutVersion", "guestToken" })
        {
            var found = Regex.Match(rated.Body, "\\"" + key + "\\"\\\\s*:\\\\s*\\"?([A-Za-z0-9_-]+)");
            if (found.Success) c.Session.Vars["wh." + key] = found.Groups[1].Value;
        }

        return StepOutcome.Success();
    }'''

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old_tail, new_tail))
print('added the shipping-rate hop')
