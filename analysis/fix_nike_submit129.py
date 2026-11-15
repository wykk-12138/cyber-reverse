import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\NikeFlow.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var res = await PostJsonAsync(c,
            $"https://api.nike.com/buy/orders/v2/US/{c.Session.CartId}/submit",
            "{}", "nike-order", ct).ConfigureAwait(false);'''

new = '''        // R129: this used to post to a hand-built `api.nike.com/buy/orders/v2/US/{id}/submit` — the
        // R87 invention. The image's only order endpoint is NikeEndpoints.OrderV5, on the guest-checkout
        // proxy host, so the cart id travels in the body instead of the path.
        var payload = new JObject
        {
            ["cartId"] = c.Session.CartId,
            ["country"] = NikeFlow.CountryCode,
        };

        var res = await PostJsonAsync(c, NikeEndpoints.OrderV5,
            payload.ToString(Newtonsoft.Json.Formatting.None), "nike-order", ct).ConfigureAwait(false);'''

if old not in t:
    raise SystemExit("submit anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("Nike submit now posts to the proven OrderV5 endpoint")
