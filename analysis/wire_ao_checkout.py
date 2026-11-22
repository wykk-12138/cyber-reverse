"""Wire the AO steps into the flow, so the class is reachable and not trimmed."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
text = io.open(FLOW, encoding='utf-8', newline='').read()

if 'AoCheckout' not in text:
    marker = 'public virtual async Task<StepOutcome> SubmitCustomerAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        raise SystemExit('SubmitCustomerAsync not found')
    body = text.find('{', position)
    branch = '''
        // R1374: AO's contact step, when a run names it. The url and the origin are the image's; the body is the
        // caller's, because those senders carry header names rather than JSON keys.
        var aoBody = c.Session.Vars.GetValueOrDefault("ao.contactBody");
        if (!string.IsNullOrWhiteSpace(aoBody))
        {
            Newtonsoft.Json.Linq.JObject aoJson;
            try
            {
                aoJson = Newtonsoft.Json.Linq.JObject.Parse(aoBody!);
            }
            catch (Newtonsoft.Json.JsonException)
            {
                return StepOutcome.Fail("ao: ao.contactBody is not valid JSON");
            }

            var (aoData, aoError) = await AoCheckout
                .SendAsync(c, "contact", aoJson, ct).ConfigureAwait(false);
            if (aoData is null) return StepOutcome.Fail(aoError);

            c.Session.Vars["aoContact"] = aoData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }
'''
    text = text[:body + 1] + branch + text[body + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('AO branch inserted into SubmitCustomerAsync')
else:
    print('already wired')
