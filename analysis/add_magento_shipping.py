"""R1369: getShippingMethods is Magento 2's shipping-methods query, and MagentoCart is where it belongs.

Reading the document in full settles it without needing a host: it selects carrier_code, method_code, carrier_title,
method_title, amount, base_amount, available, error_message, price_excl_tax and price_incl_tax, and its address
argument uses Magento's snake_case shape (region_id, country_id, save_in_address_book). That is Magento 2 GraphQL.

One detail worth pinning: the document references $region, $regionId and the rest but declares none of them. That is
how the image carries it, and a replica that "fixed" the declaration would send a different request.

where_is.py shows MagentoCart already holds this platform's documents, so the query joins it rather than starting a
new class.

Usage: python analysis/add_magento_shipping.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x147146AB4
PATH = 'replica/src/Cybersole.Stores/Flows/MagentoCart.cs'


def bytes_at(address, size):
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        try:
            reply = json.loads(reply)
        except json.JSONDecodeError:
            reply = json.loads(reply.splitlines()[0])
    if isinstance(reply, dict):
        reply = reply.get('result', reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


def read_string(chars_va):
    length = int.from_bytes(bytes_at(chars_va - 12, 12)[8:12], 'little')
    chunks, offset = [], 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


def escape_literal(text):
    out = []
    for character in text:
        if character == '\\':
            out.append('\\\\')
        elif character == '"':
            out.append('\\"')
        elif character == '\r':
            out.append('\\r')
        elif character == '\n':
            out.append('\\n')
        elif character == '\t':
            out.append('\\t')
        else:
            out.append(character)
    return ''.join(out)


document = read_string(SOURCE)
declared = sorted(set(re.findall(r'\$(\w+)\s*:', document)))
referenced = sorted(set(re.findall(r'\$(\w+)', document)))
print('getShippingMethods: %d chars  declared=%s  referenced=%d names' %
      (len(document), declared, len(referenced)))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'ShippingMethodsDocument' in text:
    raise SystemExit('already present')

anchor = '    public const string CustomerCartDocument ='
if text.count(anchor) != 1:
    raise SystemExit('anchor matched %d times' % text.count(anchor))

block = '''    /// <summary>
    /// getShippingMethods, %d characters from 0x147146AB4. Magento 2's shipping-methods query: it selects
    /// carrier_code/method_code/carrier_title/method_title with prices, and its address argument uses Magento's
    /// snake_case shape. The document references %d variables and declares none — that is how the image carries it.
    /// </summary>
    public const string ShippingMethodsDocument = "%s";

''' % (len(document), len(referenced), escape_literal(document))

text = text.replace(anchor, block + anchor, 1)

method = '''
    /// <summary>
    /// Ask the store for its shipping methods. The endpoint is a Magento store's own /graphql, so it comes from the
    /// caller; the variables are the address the caller has.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> GetShippingMethodsAsync(
        FlowContext c, string? endpoint, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint)) return (null, "magento: no endpoint");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, endpoint!.TrimEnd('/'), Body(ShippingMethodsDocument), "magento-shipping", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "magento: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "magento: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "magento: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "magento: " + ex.GetType().Name);
        }
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + method
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('ShippingMethodsDocument and GetShippingMethodsAsync added to MagentoCart')
