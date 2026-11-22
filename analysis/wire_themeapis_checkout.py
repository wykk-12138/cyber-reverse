"""Wire the cart checkout into a step so it is not trimmed, and re-run."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
text = io.open(FLOW, encoding='utf-8', newline='').read()

if 'ThemeApisCheckout' not in text:
    marker = 'public virtual async Task<StepOutcome> ProcessCartAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        # ProcessCartAsync does not exist in this tree; fall back to the step that already owns cart work.
        marker = 'public virtual async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)'
        position = text.find(marker)
    if position < 0:
        raise SystemExit('no cart step to anchor on')

    body = text.find('{', position)
    branch = '''
        // R1373: the theme APIs cart checkout, when a run names its top-level domain. The path, the body fields and
        // the two cart types are the image's; the domain is not, so it comes from the run.
        var themeApisDomain = c.Session.Vars.GetValueOrDefault("themeapis.domain");
        if (!string.IsNullOrEmpty(themeApisDomain))
        {
            var cartType = c.Session.Vars.GetValueOrDefault("themeapis.cartType")
                           ?? ThemeApisCheckout.CartTypeShopify;
            Newtonsoft.Linq.Placeholder.CartTypeCheck(cartType);

            var body = ThemeApisCheckout.Body(
                cartType,
                null,
                c.Session.Vars.GetValueOrDefault("themeapis.locationId"),
                c.Session.Vars.GetValueOrDefault("themeapis.sourceSystem"),
                null);

            var (checkoutData, checkoutError) = await ThemeApisCheckout
                .SendAsync(c, themeApisDomain, body, ct).ConfigureAwait(false);
            if (checkoutData is null) return StepOutcome.Fail(checkoutError);

            c.Session.Vars["themeapisCheckout"] =
                checkoutData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }
'''
    # The placeholder line above was a slip; the cart type is validated by Body itself.
    branch = branch.replace('            Newtonsoft.Linq.Placeholder.CartTypeCheck(cartType);\n\n', '')
    text = text[:body + 1] + branch + text[body + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('branch inserted')
else:
    print('already wired')
