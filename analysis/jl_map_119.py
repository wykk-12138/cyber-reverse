import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\JohnLewisStepMap.cs"
t = io.open(p, encoding="utf-8").read()

# Two new steps arrived in R119; record what they pair with (or do not).
old = '''    public static readonly IReadOnlyDictionary<string, string> Pairs =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["WebHandOver"] = RetailApiFamilies.JohnLewisBff.SessionHandoverV2,'''

new = '''    public static readonly IReadOnlyDictionary<string, string> Pairs =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            // R119: FindProduct(21) and AddToCart(22) are steps of this flow, and neither has a BFF
            // endpoint — the BFF starts at the handover. They stay unmapped by construction.
            ["WebHandOver"] = RetailApiFamilies.JohnLewisBff.SessionHandoverV2,'''

if old not in t:
    raise SystemExit("pairs anchor missing")
t = t.replace(old, new, 1)

# the class doc says seventeen
t = t.replace("/// John Lewis's seventeen steps against its twelve BFF endpoints, paired in R118.",
              "/// John Lewis's nineteen steps against its twelve BFF endpoints, paired in R118/R119.", 1)
t = t.replace('"name correlation between the 17 John Lewis steps and the 12 BFF endpoints; "',
              '"name correlation between the 19 John Lewis steps and the 12 BFF endpoints; "', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("JohnLewisStepMap: notes the two cart-side steps")
