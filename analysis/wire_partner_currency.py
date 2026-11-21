"""R1336: wire the conversion in front of the approval, behind a session key a capture supplies."""

import io

PATH = 'replica/src/Cybersole.Stores/Payments/Gateways.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'PayPalPartnerCurrency' in text:
    raise SystemExit('already wired')

old = '''        var partnerToken = c.Session.Vars.GetValueOrDefault("paypal.partnerToken");
        if (!string.IsNullOrEmpty(partnerToken))
        {
            var variables = new JObject
            {
                ["token"] = partnerToken,'''

new = '''        var partnerToken = c.Session.Vars.GetValueOrDefault("paypal.partnerToken");

        // R1336: the conversion goes first when the run asks for one. The image's sender writes the middle
        // variable key as "expeirences" — the document calls it $experiences — so the request keeps that
        // spelling: correcting it would be a behaviour change dressed as housekeeping.
        if (!string.IsNullOrEmpty(partnerToken) &&
            !string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("paypal.conversionType")))
        {
            var conversionVariables = new JObject
            {
                ["token"] = partnerToken,
                ["conversionType"] = c.Session.Vars.GetValueOrDefault("paypal.conversionType"),
                ["expeirences"] = new JArray(),
            };

            var (conversion, currencyError) = await PayPalPartnerCurrency
                .ConvertAsync(c, conversionVariables, ct, c.Session.Vars.GetValueOrDefault("paypal.currencyUrl"))
                .ConfigureAwait(false);

            if (conversion is null) return PaymentResult.Fail(currencyError);
            c.Session.Vars["paypal.conversion"] = conversion.ToString(Newtonsoft.Json.Formatting.None);
        }

        if (!string.IsNullOrEmpty(partnerToken))
        {
            var variables = new JObject
            {
                ["token"] = partnerToken,'''

if text.count(old) != 1:
    raise SystemExit('anchor found %d times' % text.count(old))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('wired the conversion in front of the approval')
