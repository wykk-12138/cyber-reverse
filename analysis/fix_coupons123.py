import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\PopMartFlow.cs"
t = io.open(p, encoding="utf-8").read()

# StoreFlow has no FetchCoupons step, so this is a helper the cart read uses — not an override.
t = t.replace(
    "    /// <summary>\n    /// <c>FetchCoupons</c> — the second method of the cart class, served by the coupons list.\n    /// </summary>\n    public override async Task<StepOutcome> FetchCouponsAsync",
    "    /// <summary>\n    /// <c>FetchCoupons</c> — the second method of the cart class, served by the coupons list.\n    ///\n    /// <para>\n    /// A private helper rather than an override: <c>StoreFlow</c> has no <c>FetchCoupons</c> step, and\n    /// inventing one would put a step in the vocabulary that the binary does not ask for. The cart\n    /// read calls it, so the behaviour exists without the invented step.\n    /// </para>\n    /// </summary>\n    private async Task<StepOutcome> FetchCouponsAsync", 1)

# call it from the cart read
old_tail = '''        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }'''
new_tail = '''        c.Session.Vars["cart"] = res.Body;

        // the cart class reads the cart and then the coupons; keep that order
        await FetchCouponsAsync(c, ct).ConfigureAwait(false);
        return StepOutcome.Success();
    }'''
if old_tail not in t:
    raise SystemExit("cart tail anchor missing")
t = t.replace(old_tail, new_tail, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("FetchCoupons is a helper called by the cart read")
