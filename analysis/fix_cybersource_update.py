"""Tidy the update branch's indentation, and add tests for the update path."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/CybersourcePaymentTests.cs'

flow = io.open(FLOW, encoding='utf-8', newline='').read()

old = '''                        if (c.Session.Vars.GetValueOrDefault("cybersource.updateMode") == "true")
            {
                var (updateData, updateError) = await Cybersole.Stores.Payments.CybersourcePayment
                    .UpdateAsync(c, cybersourceEndpoint, paymentVariables, ct).ConfigureAwait(false);
                if (updateData is null) return StepOutcome.Fail(updateError);

                c.Session.Vars["cybersourceUpdate"] =
                    updateData.ToString(Newtonsoft.Json.Formatting.None);
            }

return StepOutcome.Success();'''

new = '''            if (c.Session.Vars.GetValueOrDefault("cybersource.updateMode") == "true")
            {
                var (updateData, updateError) = await Cybersole.Stores.Payments.CybersourcePayment
                    .UpdateAsync(c, cybersourceEndpoint, paymentVariables, ct).ConfigureAwait(false);
                if (updateData is null) return StepOutcome.Fail(updateError);

                c.Session.Vars["cybersourceUpdate"] =
                    updateData.ToString(Newtonsoft.Json.Formatting.None);
            }

            return StepOutcome.Success();'''

if old not in flow:
    raise SystemExit('branch not found as inserted')
flow = flow.replace(old, new, 1)
io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
print('indentation fixed')

tests = io.open(TESTS, encoding='utf-8').read()
if 'TheUpdateIsTheSameFamilys' not in tests:
    block = '''
    /// <summary>
    /// R1376: updateMyPaymentWithActions is the same family's update — same handler, same refusal, three declared
    /// variables of its own.
    /// </summary>
    [Fact]
    public void TheUpdateIsTheSameFamilys()
    {
        Assert.Equal(401, CybersourcePayment.UpdatePaymentDocument.Length);
        Assert.StartsWith("mutation updateMyPaymentWithActions", CybersourcePayment.UpdatePaymentDocument);
        Assert.Contains("$actions", CybersourcePayment.UpdatePaymentDocument);
        Assert.Contains("$id", CybersourcePayment.UpdatePaymentDocument);
        Assert.Contains("$version", CybersourcePayment.UpdatePaymentDocument);
    }

    /// <summary>Without a capture context the update refuses before sending, like the create.</summary>
    [Fact]
    public async Task TheUpdateRefusesWithoutACaptureContext()
    {
        var (data, error) = await CybersourcePayment.UpdateAsync(
            new Cybersole.Stores.Flows.FlowContext(), null, new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no endpoint", error);

        var (second, secondError) = await CybersourcePayment.UpdateAsync(
            new Cybersole.Stores.Flows.FlowContext { Http = new Cybersole.Http.NetClient(), Url = "https://x.test/" },
            "https://x.test", new JObject(), default);

        Assert.Null(second);
        Assert.Equal(CybersourcePayment.NoCaptureContextMessage, secondError);
    }
}
'''

    tests = tests.rstrip()
    tests = tests[:tests.rfind('}')].rstrip('\n') + '\n' + block
    io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
    print('appended two update tests')
