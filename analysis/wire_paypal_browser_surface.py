"""R1379b: wire the browser surface so it exists in the product, and mirror how the hash family sets headers.

`c.Session.Headers[name] = value` is the project's mechanism — GraphQlHashQueries uses it for x-graphql-hash. The
browser surface sets its session headers the same way and then posts, which also gives the class a production caller so
the trimmer keeps it (R1370's lesson: a class with only tests calling it does not survive).
"""
import io
import sys

sys.path.insert(0, 'analysis')
from insert_into_class import insert_before_class_end  # noqa: E402

MODEL = 'replica/src/Cybersole.Stores/Payments/PayPalBrowserSurface.cs'
GATEWAY = 'replica/src/Cybersole.Stores/Payments/Gateways.cs'

model = io.open(MODEL, encoding='utf-8', newline='').read()

if 'SendAsync' not in model:
    method = '''
    /// <summary>
    /// Send the browser path's request. The session values are applied as headers first, the way the hash family does
    /// it, and a session without them is refused before anything leaves.
    /// </summary>
    public static async System.Threading.Tasks.Task<(JObject? Data, string Error)> SendAsync(
        Cybersole.Stores.Flows.FlowContext c, string document, string? token, bool withSplitTender,
        string? euat, string? clientMetadataId, string? cookie,
        System.Threading.CancellationToken ct)
    {
        var (usable, reason) = CanSend(euat, clientMetadataId);
        if (!usable) return (null, reason);

        c.Session.Headers["x-app-name"] = AppName;
        c.Session.Headers["x-paypal-internal-euat"] = euat!;
        c.Session.Headers["paypal-client-metadata-id"] = clientMetadataId!;
        c.Session.Headers["accept-language"] = AcceptLanguage;
        if (!string.IsNullOrEmpty(cookie)) c.Session.Headers["cookie"] = cookie!;

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, Origin + "/graphql", Body(document, token, withSplitTender), "paypal-browser", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "browser surface: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "browser surface: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (System.Exception ex)
        {
            return (null, "browser surface: " + ex.GetType().Name);
        }
    }
'''

    model = insert_before_class_end(model, 'public static class PayPalBrowserSurface', method)
    io.open(MODEL, 'w', encoding='utf-8', newline='').write(model)
    print('SendAsync added inside the class')

gateway = io.open(GATEWAY, encoding='utf-8', newline='').read()
if 'PayPalBrowserSurface' not in gateway:
    marker = 'public static async Task<(JObject? Data, string Error)> ApproveAsync'
    position = gateway.find(marker)
    if position < 0:
        marker = 'public const string BaseUrl'
        position = gateway.find(marker)
    if position < 0:
        raise SystemExit('no anchor in Gateways.cs')

    anchor_end = gateway.find(';', position) + 1
    note = '''
    /// <summary>
    /// R1379: the browser-side PayPal path is reachable from here, so it is part of the product rather than a class
    /// only its tests know about. A session without the two page values gets the reason instead of a request.
    /// </summary>
    public static Task<(JObject? Data, string Error)> SendBrowserSideAsync(
        Cybersole.Stores.Flows.FlowContext c, string document, string? token, bool withSplitTender,
        string? euat, string? clientMetadataId, string? cookie, CancellationToken ct) =>
        PayPalBrowserSurface.SendAsync(c, document, token, withSplitTender, euat, clientMetadataId, cookie, ct);
'''
    gateway = gateway[:anchor_end] + note + gateway[anchor_end:]
    io.open(GATEWAY, 'w', encoding='utf-8', newline='').write(gateway)
    print('gateway gained the browser-side entry point')
