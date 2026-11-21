"""R1332: a billing step that reports success and sends nothing.

ShopifyFlow.SubmitBillingAsync is eight lines: resolve an address, write two session keys, return Success.
There is no request in it. So the run log says billing completed, the checkout is untouched, and the failure
surfaces later as a payment error with no cause attached.

The endpoint is not captured, so inventing one is the wrong repair. What can be repaired is the report: the step
says that no billing request was made and why, the same way the Casio sku gap and the Warhammer onboarding hop
do. A step that did nothing should be distinguishable from one that succeeded.

Usage: python analysis/fix_shopify_billing.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'no billing request' in text:
    raise SystemExit('already honest')

old = '''        var bill = c.Billing ?? c.Shipping ?? AddressFromProfile(c);
        if (bill is null) return StepOutcome.Fail("shopify: no billing address");
        c.Session.Vars["billing1"] = bill.Address1 ?? string.Empty;
        c.Session.Vars["billingZip"] = bill.ZipCode ?? string.Empty;
        return StepOutcome.Success();'''

new = '''        var bill = c.Billing ?? c.Shipping ?? AddressFromProfile(c);
        if (bill is null) return StepOutcome.Fail("shopify: no billing address");

        c.Session.Vars["billing1"] = bill.Address1 ?? string.Empty;
        c.Session.Vars["billingZip"] = bill.ZipCode ?? string.Empty;

        // R1332: this step used to return Success here without sending anything, so a run log said billing was
        // done while the checkout had not been touched — the failure then surfaced as a payment error with no
        // cause attached. The endpoint is not captured, and inventing one is worse than saying so: the address
        // is recorded for a consumer that does have it, and the step reports what it did not do.
        c.Session.Vars["shopify.billingSubmitted"] = "false";
        c.Emit("shopify: billing address recorded but no billing request was made — the checkout billing " +
               "endpoint is not captured, so nothing was submitted", "StatusInfo");
        return StepOutcome.Success();'''

if text.count(old) != 1:
    raise SystemExit('billing body found %d times' % text.count(old))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('SubmitBillingAsync now reports that it submits nothing')
