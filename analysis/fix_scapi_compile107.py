import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareFlow.cs"
t = io.open(p, encoding="utf-8").read()

# 1) Newtonsoft is not imported in this file — use the fully qualified name like the rest of the flow
#    does elsewhere (Formatting.None is already qualified).
t = t.replace('basketId = JObject.Parse(created.Body)["basketId"]?.ToString();',
              'basketId = Newtonsoft.Json.Linq.JObject.Parse(created.Body)["basketId"]?.ToString();')

t = t.replace('''            var body = new JObject
            {
                ["productId"] = c.Session.VariantId,
                ["quantity"] = c.Session.Quantity,
            };''',
              '''            var body = new Newtonsoft.Json.Linq.JObject
            {
                ["productId"] = c.Session.VariantId,
                ["quantity"] = c.Session.Quantity,
            };''')

# 2) SiteId is a property on this flow, not a method.
t = t.replace('Uri.EscapeDataString(SiteId(c))', 'Uri.EscapeDataString(SiteId)')

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("qualified JObject and used the SiteId property")
