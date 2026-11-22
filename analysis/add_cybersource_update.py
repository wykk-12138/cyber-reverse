"""R1376: the last unlanded GraphQL operation — updateMyPaymentWithActions — joins its Cybersource sibling.

R1364 read its handler: cybersource, isv_payment_data, isv_store, isv_screenHeight, isv_screenWidth,
isv_customerIpAddress, creditCardWithPayerAuthentication, centAmount, currencyCode, customFields, "No capture context".
R1371 landed createMyPayment on that evidence; this is the same family's update, and its document is 401 characters at
0x1470FD05C.

Usage: python analysis/add_cybersource_update.py
"""
import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470FD05C
PATH = 'replica/src/Cybersole.Stores/Payments/CybersourcePayment.cs'
FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
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
    chunks, offset = [], 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


def dotnet_verbatim(text):
    return text.replace('"', '""')


document = read_string(SOURCE)
declared = sorted(set(re.findall(r'\$(\w+)\s*:', document)))
print('updateMyPaymentWithActions: %d chars  declares %s' % (len(document), declared))

docs = json.loads(io.open(DOCS, encoding='utf-8').read())
docs['update_my_payment_with_actions'] = document
io.open(DOCS, 'w', encoding='utf-8', newline='').write(
    json.dumps(docs, ensure_ascii=False, indent=1, sort_keys=True))

text = io.open(PATH, encoding='utf-8', newline='').read()
if 'UpdatePaymentDocument' in text:
    raise SystemExit('already present')

anchor = '    /// <summary>The provider name the handler carries.</summary>'
if text.count(anchor) != 1:
    raise SystemExit('anchor matched %d times' % text.count(anchor))

block = '''    /// <summary>
    /// updateMyPaymentWithActions, %s characters from 0x1470FD05C — the same family's update, sent by the handler
    /// at 0x140E55A00 that R1364 read. Declares %s.
    /// </summary>
    public const string UpdatePaymentDocument = @"%s";

''' % (len(document), ', '.join('$' + n for n in declared), dotnet_verbatim(document))

text = text.replace(anchor, block + anchor, 1)

method = '''
    /// <summary>
    /// Send the update. Same endpoint rule as the create: the merchant host is the caller's, and a payment without a
    /// capture context is refused before it leaves.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> UpdateAsync(
        FlowContext c, string? endpoint, JObject variables, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint))
            return (null, "cybersource: no endpoint — the merchant host is the caller's");

        if (variables?["customFields"]?["isv_payment_data"] is null)
            return (null, NoCaptureContextMessage);

        try
        {
            var body = new JObject
            {
                ["operationName"] = "updateMyPaymentWithActions",
                ["query"] = UpdatePaymentDocument,
                ["variables"] = variables,
            };

            var reply = await GatewayHttp
                .PostAsync(c, endpoint!.TrimEnd('/'), body, "cybersource-update", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, ErrorProcessingPaymentMessage);

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, ErrorProcessingPaymentMessage);

            var data = reply["data"] as JObject;
            return data is null ? (null, ErrorProcessingPaymentMessage) : (data, string.Empty);
        }
        catch (Exception)
        {
            return (null, ErrorProcessingPaymentMessage);
        }
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\\n') + method
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('UpdatePaymentDocument and UpdateAsync added')

flow = io.open(FLOW, encoding='utf-8', newline='').read()
if 'UpdateAsync' not in flow:
    marker = '            var (paymentData, paymentError) = await Cybersole.Stores.Payments.CybersourcePayment'
    position = flow.find(marker)
    if position < 0:
        raise SystemExit('cybersource branch not found in the flow')
    end = flow.find('return StepOutcome.Success();', position)
    insert = '''            return StepOutcome.Success();

            // (the update path is reached through cybersource.updateMode, set below)
'''
    # Simpler: add a second branch right before the existing return.
    branch = '''            if (c.Session.Vars.GetValueOrDefault("cybersource.updateMode") == "true")
            {
                var (updateData, updateError) = await Cybersole.Stores.Payments.CybersourcePayment
                    .UpdateAsync(c, cybersourceEndpoint, paymentVariables, ct).ConfigureAwait(false);
                if (updateData is null) return StepOutcome.Fail(updateError);

                c.Session.Vars["cybersourceUpdate"] =
                    updateData.ToString(Newtonsoft.Json.Formatting.None);
            }

'''
    flow = flow[:end] + branch + flow[end:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
    print('update branch added to the flow')
