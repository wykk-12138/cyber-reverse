"""R1328: give the Warhammer API host the same session seam the rest of the flow already uses.

PostJsonAsync is handed ApiHost + "/graphql", an absolute URL, so nothing can redirect it in a test. Other
flows in this file already read their hosts through a seam (`Seam("paypal3ds.heliosServerDataUrl", …)`), and
the session override is the established way to point a flow at a capture or a test server. This adds the same
one-line seam for the Warhammer host — it does not change the default.

Usage: python analysis/add_wh_host_seam.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'wh.apiHost' in text:
    raise SystemExit('seam already present')

old = '            var onboarded = await PostJsonAsync(c, ApiHost + "/graphql",'
new = ('            var onboarded = await PostJsonAsync(c, ApiHostFor(c) + "/graphql",')
if text.count(old) != 1:
    raise SystemExit('onboarding post site found %d times' % text.count(old))
text = text.replace(old, new)

old_approve = '        var res = await PostJsonAsync(c, ApiHost + "/graphql",\n            body.ToString(Newtonsoft.Json.Formatting.None), "wh-payment", ct).ConfigureAwait(false);'
new_approve = '        var res = await PostJsonAsync(c, ApiHostFor(c) + "/graphql",\n            body.ToString(Newtonsoft.Json.Formatting.None), "wh-payment", ct).ConfigureAwait(false);'
if text.count(old_approve) != 1:
    raise SystemExit('approval post site found %d times' % text.count(old_approve))
text = text.replace(old_approve, new_approve)

anchor = '    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)\n    {\n        ApplyWaf(c);\n\n        if (!c.Session.Vars.TryGetValue("paymentToken"'
if text.count(anchor) != 1:
    raise SystemExit('SubmitPaymentAsync anchor found %d times' % text.count(anchor))

helper = (
    '    /// <summary>\n'
    '    /// The store\'s API host, with a session override — the same seam other flows in this file use so a\n'
    '    /// capture or a test can point the flow somewhere else without a rebuild. The default is unchanged.\n'
    '    /// </summary>\n'
    '    private static string ApiHostFor(FlowContext c) =>\n'
    '        c.Session.Vars.TryGetValue("wh.apiHost", out var host) && !string.IsNullOrEmpty(host) ? host : ApiHost;\n'
    '\n'
)
text = text.replace(anchor, helper + anchor)

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('added the wh.apiHost seam and routed both posts through it')
