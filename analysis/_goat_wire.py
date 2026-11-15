import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("goat: no purchase to submit");'''
new = '''        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("goat: no purchase to submit");

        // R328: a GOAT purchase is keyed to a saved address, and the image has an endpoint for exactly that list.
        // Fail early with a clear message instead of letting the confirm call 4xx without explanation.
        if (!await EnsureAddressAsync(c, ct).ConfigureAwait(false))
            return StepOutcome.Fail("goat: no saved address on this account", retryable: true);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('SubmitOrderAsync now ensures an address first')
