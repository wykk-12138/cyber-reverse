"""R1335: wire the partner approval into the gateway's authorize step, behind a session key a capture supplies."""

import io

PATH = 'replica/src/Cybersole.Stores/Payments/Gateways.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'PayPalPartnerApprove' in text:
    raise SystemExit('already wired')

old = '''    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var orderId = c.Session.Vars.TryGetValue("paypal.orderId", out var o) ? o : null;
        if (string.IsNullOrEmpty(orderId)) return await TokenizeAsync(c, ct).ConfigureAwait(false);'''

new = '''    public async Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        // R1335: the partner approval, when the run carries a buyer token for it. The image's own sender fills
        // eleven variables and this class does not invent the seven it cannot know — the caller puts them in
        // the session, and without the token the step falls through to the paths below unchanged.
        var partnerToken = c.Session.Vars.GetValueOrDefault("paypal.partnerToken");
        if (!string.IsNullOrEmpty(partnerToken))
        {
            var variables = new JObject
            {
                ["token"] = partnerToken,
                ["selectedAddressId"] = c.Session.Vars.GetValueOrDefault("paypal.selectedAddressId"),
                ["preferredShippingAddressId"] = c.Session.Vars.GetValueOrDefault("paypal.preferredShippingAddressId"),
                ["selectedFundingOptionId"] = c.Session.Vars.GetValueOrDefault("paypal.selectedFundingOptionId"),
                ["preferredFundingOptionId"] = c.Session.Vars.GetValueOrDefault("paypal.preferredFundingOptionId"),
                ["preAuthorizationRequired"] = false,
                ["fundingMethodType"] = c.Session.Vars.GetValueOrDefault("paypal.fundingMethodType")
                    ?? PayPalPartnerApprove.FundingMethodIframe,
                ["setStickyFiRequired"] = false,
                ["scaCompleted"] = true,
            };

            var (data, error) = await PayPalPartnerApprove
                .ApproveAsync(c, variables, ct, c.Session.Vars.GetValueOrDefault("paypal.partnerApproveUrl"))
                .ConfigureAwait(false);

            if (data is null) return PaymentResult.Fail(error);

            var state = data["approveMemberPayment"]?["state"]?.ToString();
            c.Session.Vars["paypal.approveState"] = state ?? string.Empty;
            var paymentId = data["approveMemberPayment"]?["cart"]?["paymentId"]?.ToString();
            if (!string.IsNullOrEmpty(paymentId)) c.Session.PaymentMethodId = paymentId;

            return string.Equals(state, "COMPLETED", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(state, "APPROVED", StringComparison.OrdinalIgnoreCase)
                ? PaymentResult.Success(paymentId ?? partnerToken)
                : PaymentResult.Fail($"paypal: approve state {state}");
        }

        var orderId = c.Session.Vars.TryGetValue("paypal.orderId", out var o) ? o : null;
        if (string.IsNullOrEmpty(orderId)) return await TokenizeAsync(c, ct).ConfigureAwait(false);'''

if text.count(old) != 1:
    raise SystemExit('authorize anchor found %d times' % text.count(old))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('wired the partner approval into PayPalGateway.AuthorizeAsync')
