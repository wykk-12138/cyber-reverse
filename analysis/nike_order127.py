import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\NikeEndpoints.cs"
t = io.open(p, encoding="utf-8").read()

anchor = t.rstrip()
if "OrderV5" in t:
    print("already present")
else:
    # insert before the closing brace of the class: find the last "}" and put the member above it
    idx = anchor.rfind("}")
    addition = '''
    /// <summary>
    /// The order endpoint — <c>https://www.nike.com/gs/checkout-api/api/v5/Order/</c>.
    ///
    /// <para>
    /// Found in R127 while checking a <c>v5/Order/</c> path that had been wrongly attributed to
    /// Scheels. It is Nike's, and it is the answer to a question this session asked repeatedly
    /// (R87: where does an order go?). The host is not <c>api.nike.com</c> but
    /// <c>www.nike.com/gs/checkout-api/api</c> — the guest-checkout proxy — which is why the endpoint
    /// never turned up in the <c>api.nike.com</c> family.
    /// </para>
    /// </summary>
    public const string OrderV5 = "https://www.nike.com/gs/checkout-api/api/v5/Order/";
'''
    t = anchor[:idx] + addition + anchor[idx:]
    t = t.rstrip() + "\n"
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("Nike OrderV5 added")
