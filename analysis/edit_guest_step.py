"""The guest step, edited on the restored file: replace one expression-bodied member, nothing else."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
text = io.open(FLOW, encoding='utf-8', newline='').read()

old = '''    public virtual Task<StepOutcome> GuestCallbackAsync(FlowContext c, CancellationToken ct)
        => NotSupported("GuestCallback");'''

new = '''    public virtual async Task<StepOutcome> GuestCallbackAsync(FlowContext c, CancellationToken ct)
    {
        // R1353: On Running's guest checkout, when the run asks for it. Its endpoint is the one the store table
        // already held; before this, nothing used that string.
        var guestEmail = c.Session.Vars.GetValueOrDefault("onRunning.guestEmail") ?? c.ProfileData?.Email;
        if (!string.IsNullOrEmpty(guestEmail) &&
            string.Equals(c.Session.Vars.GetValueOrDefault("onRunning.guest"), "true",
                StringComparison.OrdinalIgnoreCase))
        {
            var (guestData, guestError) = await OnRunningGraphQl
                .CheckoutAsGuestAsync(c, new Newtonsoft.Json.Linq.JObject { ["email"] = guestEmail }, ct)
                .ConfigureAwait(false);
            if (guestData is null) return StepOutcome.Fail(guestError);

            c.Session.Vars["guestCheckout"] = guestData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

        return NotSupported("GuestCallback");
    }'''

if text.count(old) != 1:
    raise SystemExit('guest step found %d times' % text.count(old))
if 'NotSupported("GuestCallback");' in text.replace(old, ''):
    raise SystemExit('another GuestCallback return exists')

io.open(FLOW, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('replaced exactly one member')
