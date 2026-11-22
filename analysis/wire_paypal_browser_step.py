"""R1379c: reach the browser surface from the PayPal step, so it is in the product and not just in a test."""

import io
import sys

sys.path.insert(0, 'analysis')
from insert_into_class import class_body_end  # noqa: E402

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
flow = io.open(FLOW, encoding='utf-8', newline='').read()

if 'PayPalBrowserSurface' in flow:
    raise SystemExit('already wired')

marker = 'public virtual async Task<StepOutcome> SubmitPayPalAsync(FlowContext c, CancellationToken ct)'
position = flow.find(marker)
if position < 0:
    raise SystemExit('SubmitPayPalAsync not found')

body = flow.find('{', position)
branch = '''
        // R1379: the browser-side PayPal path, when a run holds the two page values it needs. Those two are the
        // session's; the app name, the headers and the body shape are the image's.
        var browserEuat = c.Session.Vars.GetValueOrDefault("paypal.browserEuat");
        var browserMetadata = c.Session.Vars.GetValueOrDefault("paypal.clientMetadataId");
        if (!string.IsNullOrEmpty(browserEuat) && !string.IsNullOrEmpty(browserMetadata))
        {
            var (browserData, browserError) = await Cybersole.Stores.Payments.PayPalBrowserSurface
                .SendAsync(c, Cybersole.Stores.Payments.PayPalPartnerApprove.Document,
                    c.Session.Vars.GetValueOrDefault("paypal.token"), true,
                    browserEuat, browserMetadata, c.Session.Vars.GetValueOrDefault("paypal.cookie"), ct)
                .ConfigureAwait(false);
            if (browserData is null) return StepOutcome.Fail(browserError);

            c.Session.Vars["paypalBrowser"] = browserData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }
'''
flow = flow[:body + 1] + branch + flow[body + 1:]
io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
print('browser branch inserted into SubmitPayPalAsync')
