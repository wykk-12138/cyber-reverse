"""R1334: encode the cartApi endpoint rule, and let every MagentoCart call honour it.

R1333 found the path (/cartApi/checkout, one code reference) and the two host labels (www, themeapis) but not
the rule joining them. This round read the composition:

    v42 = sub_141E541B0()                                   // an instance property: the request's host
    v43 = sub_141CF82E0(v42, "www", "themeapis")            // the host with www replaced by themeapis
    v44 = sub_141CF62D0("https://", v43, "/cartApi/checkout")

and the same function's literals include `https://themeapis.` (0x14708885C), which is what the replacement
produces for a host that carries no `www.` at all.

So the endpoint is https://<host, www→themeapis>/cartApi/checkout. The rule now lives in MagentoCart, and the six
methods that take an endpoint pass it through ResolveEndpoint first: a caller that hands in a full URL — which is
every caller today — gets exactly what it passed, and a caller that hands in a bare host gets the composed
cartApi URL instead of a URL that cannot work.

Usage: python analysis/add_cartapi_endpoint.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/MagentoCart.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'CartApiPath' in text:
    raise SystemExit('already present')

anchor = '    /// <summary>The three tokens the add mutation substitutes.</summary>'
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

block = (
    '    /// <summary>\n'
    '    /// The cart-API path the observed family posts to — 0x146AB27FC, one code reference in the whole\n'
    '    /// <c>.text</c> (<c>sub_140C32160</c>).\n'
    '    /// </summary>\n'
    '    public const string CartApiPath = "/cartApi/checkout";\n'
    '\n'
    '    /// <summary>\n'
    '    /// The cart-API endpoint for a host. The image composes it as\n'
    '    /// <c>"https://" + host-with-www-replaced-by-themeapis + "/cartApi/checkout"</c> — <c>sub_141CF82E0(host,\n'
    '    /// "www", "themeapis")</c> at 0x140C32471, and the literal <c>https://themeapis.</c> at 0x14708885C is what\n'
    '    /// that produces for a host with no <c>www.</c> prefix.\n'
    '    /// </summary>\n'
    '    public static string CartApiEndpointFor(string hostOrOrigin)\n'
    '    {\n'
    '        var host = hostOrOrigin.TrimEnd(\'/\');\n'
    '        if (host.Contains("://", StringComparison.Ordinal))\n'
    '            host = host[(host.IndexOf("://", StringComparison.Ordinal) + 3)..];\n'
    '\n'
    '        return "https://" + host.Replace("www.", "themeapis.", StringComparison.OrdinalIgnoreCase) + CartApiPath;\n'
    '    }\n'
    '\n'
    '    /// <summary>\n'
    '    /// An endpoint as given, or composed from a bare host. Callers that pass a full URL — every caller today —\n'
    '    /// get back exactly what they passed; a bare host would otherwise produce a request to nowhere.\n'
    '    /// </summary>\n'
    '    public static string ResolveEndpoint(string endpointOrHost) =>\n'
    '        endpointOrHost.Contains("://", StringComparison.Ordinal)\n'
    '            ? endpointOrHost\n'
    '            : CartApiEndpointFor(endpointOrHost);\n'
    '\n'
)

text = text.replace(anchor, block + anchor)

# Route the six entry points through the resolver.
import re

count = 0
for method in ('CreateEmptyAsync', 'AddProductAsync', 'SetBillingAsync', 'AddPaymentAsync',
               'SubmitOrderAsync', 'ReadCartAsync'):
    signature = 'public static async Task<'
    index = text.find(' ' + method + '(')
    if index < 0:
        continue
    body_start = text.find('{', index)
    brace = text.find('endpoint', body_start)
    # Insert one normalisation at the top of the method body.
    text = text[:body_start + 1] + (
        '\n        endpoint = ResolveEndpoint(endpoint);'
    ) + text[body_start + 1:]
    count += 1

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('added CartApiPath, CartApiEndpointFor, ResolveEndpoint; normalised %d methods' % count)
