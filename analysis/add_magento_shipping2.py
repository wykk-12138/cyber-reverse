"""R1369 (second attempt): insert into MagentoCart with real brace matching.

The first attempt cut at the file's last brace, which put the method outside the class. This walks the class body from
its declaration, skipping string literals and comments, so the insertion lands just before the brace that actually
closes MagentoCart.

Usage: python analysis/add_magento_shipping2.py
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


def class_body_end(source, declaration):
    """Index of the brace that closes the class, walking past strings and comments."""
    start = source.find(declaration)
    if start < 0:
        raise SystemExit('declaration not found')
    index = source.find('{', start)
    depth = 0
    while index < len(source):
        character = source[index]
        if character == '"':
            index += 1
            while index < len(source):
                if source[index] == '\\':
                    index += 2
                    continue
                if source[index] == '"':
                    break
                index += 1
        elif character == '/' and source.startswith('//', index):
            index = source.find('\n', index)
            if index < 0:
                break
        elif character == '{':
            depth += 1
        elif character == '}':
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise SystemExit('unbalanced class body')


document = read_string(SOURCE)
referenced = sorted(set(re.findall(r'\$(\w+)', document)))
print('getShippingMethods: %d chars  referenced %d variables, declared 0' % (len(document), len(referenced)))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'ShippingMethodsDocument' in text:
    raise SystemExit('already present')

anchor = '    public const string CustomerCartDocument ='
if text.count(anchor) != 1:
    raise SystemExit('anchor matched %d times' % text.count(anchor))

block = '''    /// <summary>
    /// getShippingMethods, %d characters from 0x147146AB4. Magento 2's shipping-methods query: carrier_code,
    /// method_code, carrier_title and method_title with prices, and an address argument in Magento's snake_case
    /// shape. It references %d variables and declares none — the image carries it that way, and "fixing" the
    /// declaration would send a different request.
    /// </summary>
    public const string ShippingMethodsDocument = "%s";

''' % (len(document), len(referenced), escape_literal(document))

text = text.replace(anchor, block + anchor, 1)

method = '''
    /// <summary>
    /// Ask the store for its shipping methods. The endpoint is a Magento store's own /graphql, so it comes from the
    /// caller, as do the address variables.
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
'''

close = class_body_end(text, 'public static class MagentoCart')
text = text[:close] + method + text[close:]
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('constant and method inserted inside MagentoCart (close brace at %d)' % close)
