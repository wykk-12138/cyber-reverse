"""R1359: four B-block operations have handlers with no host — one family, one class, origin from the caller.

getCustomerInformation's handler (0x140E5B940) holds nothing but application/json and the envelope keys, and so does
updateMyPaymentWithActions' (0x140E5B570) a few hundred bytes earlier. Both sit in the 0x140E5B5xx block with
getCart's state machine, which means one family whose origin lives above them — the same situation as the api/graphql
block in R1345, and answered the same way: take the origin from the caller and refuse without one.

Four operations go in: getCustomerInformation (197), getPaymentdMethods (3067), item (67) and getCart (3234).

Usage: python analysis/add_store_session_queries.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SITES = {
    'getCustomerInformation': 0x147144F7C,
    'getPaymentdMethods': 0x14714511C,
    'item': 0x147146EF4,
    'getCart': 0x14714361C,
}
OUT = 'replica/src/Cybersole.Stores/Flows/StoreSessionQueries.cs'
DOCS = 'analysis/.block_a_docs.json'


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
    chunks = []
    offset = 0
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


documents = {}
declared = {}
for name, address in SITES.items():
    text = read_string(address)
    documents[name] = text
    declared[name] = sorted(set(re.findall(r'\$(\w+)\s*:', text)))
    print('%-22s %5d chars  declares %s' % (name, len(text), declared[name]))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
for name, text in documents.items():
    docs['session_' + name] = text
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))


def array(names):
    return 'new[] { ' + ', '.join('"%s"' % n for n in names) + ' }' if names else 'Array.Empty<string>()'


source = '''using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Four session-shaped operations whose handlers name no host.
///
/// <para>
/// <b>Observed</b> (R1359): the handlers for <c>getCustomerInformation</c> (sub_140E5B940) and
/// <c>updateMyPaymentWithActions</c> (sub_140E5B570) hold only <c>application/json</c> and the envelope keys, and they
/// sit in the same address block as <c>getCart</c>'s state machine. Nothing in the block carries a host, so the origin
/// belongs to the caller — sending a relative path to a guessed host would be worse than refusing.
/// </para>
///
/// <para>
/// <b>Observed:</b> the declared sets differ per operation and are published as measured:
/// getCustomerInformation %(declared_customer)s, getPaymentdMethods %(declared_payment)s, item %(declared_item)s,
/// getCart %(declared_cart)s.
/// </para>
/// </summary>
public static class StoreSessionQueries
{
    /// <summary>getCustomerInformation, 197 characters from 0x147144F7C.</summary>
    public const string GetCustomerInformationDocument = "%(doc_customer)s";

    /// <summary>getPaymentdMethods, 3067 characters from 0x14714511C — the operation's own misspelling.</summary>
    public const string GetPaymentdMethodsDocument = "%(doc_payment)s";

    /// <summary>item, 67 characters from 0x147146EF4.</summary>
    public const string ItemDocument = "%(doc_item)s";

    /// <summary>getCart, 3234 characters from 0x14714361C.</summary>
    public const string GetCartDocument = "%(doc_cart)s";

    /// <summary>The variables each document declares.</summary>
    public static readonly IReadOnlyDictionary<string, string[]> Declared = new Dictionary<string, string[]>
    {
        ["getCustomerInformation"] = %(array_customer)s,
        ["getPaymentdMethods"] = %(array_payment)s,
        ["item"] = %(array_item)s,
        ["getCart"] = %(array_cart)s,
    };

    /// <summary>The document for an operation, or null when it is not one of the four.</summary>
    public static string? DocumentFor(string operation) => operation switch
    {
        "getCustomerInformation" => GetCustomerInformationDocument,
        "getPaymentdMethods" => GetPaymentdMethodsDocument,
        "item" => ItemDocument,
        "getCart" => GetCartDocument,
        _ => null,
    };

    /// <summary>The request body.</summary>
    public static JObject Envelope(string operation, JObject variables) => new()
    {
        ["operationName"] = operation,
        ["query"] = DocumentFor(operation) ?? throw new ArgumentOutOfRangeException(nameof(operation)),
        ["variables"] = variables,
    };

    /// <summary>Post one operation; every variable must be one the document declares.</summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? origin, string operation, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "store-session: no origin");
        var document = DocumentFor(operation);
        if (document is null) return (null, "store-session: unknown operation " + operation);

        foreach (var property in variables.Properties())
        {
            if (Array.IndexOf(Declared[operation], property.Name) >= 0) continue;
            return (null, "store-session: " + operation + " does not declare $" + property.Name);
        }

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, origin!.TrimEnd('/'), Envelope(operation, variables), "store-session", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, operation + ": no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, operation + ": " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, operation + ": no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, operation + ": " + ex.GetType().Name);
        }
    }
}
''' % {
    'declared_customer': declared['getCustomerInformation'],
    'declared_payment': declared['getPaymentdMethods'],
    'declared_item': declared['item'],
    'declared_cart': declared['getCart'],
    'doc_customer': escape_literal(documents['getCustomerInformation']),
    'doc_payment': escape_literal(documents['getPaymentdMethods']),
    'doc_item': escape_literal(documents['item']),
    'doc_cart': escape_literal(documents['getCart']),
    'array_customer': array(declared['getCustomerInformation']),
    'array_payment': array(declared['getPaymentdMethods']),
    'array_item': array(declared['item']),
    'array_cart': array(declared['getCart']),
}

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)
