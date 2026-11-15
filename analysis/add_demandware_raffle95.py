import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareControllers.cs"
t = io.open(p, encoding="utf-8").read()

# R95: the raffle/sale-entry chain and the confirmed URL shape.
old = '''    // ---- payment
    public const string AdyenAuthorize = "AdyenUpgrade-Authorize";'''
new = '''    // ---- payment
    public const string AdyenAuthorize = "AdyenUpgrade-Authorize";

    // ---- raffle / sale entry (R95, from the full URL templates)
    public const string SaleSignupSubmit = "SaleRegistration-SignupSubmit";
    public const string SaleConfig = "SaleRegistration-Config";'''

if old not in t:
    raise SystemExit("payment anchor missing")
t = t.replace(old, new, 1)

# extend All with the two new controllers
old_all = "        AccountLogin, CsrfGenerate, ProductVariation, ProductShow, WishlistAddToCart,\n        AdyenAuthorize,"
new_all = ("        AccountLogin, CsrfGenerate, ProductVariation, ProductShow, WishlistAddToCart,\n"
           "        AdyenAuthorize, SaleSignupSubmit, SaleConfig,")
if old_all not in t:
    raise SystemExit("All anchor missing")
t = t.replace(old_all, new_all, 1)

extra = '''
    /// <summary>
    /// The store host each site id belongs to, where the image spells both out. Only the three the
    /// image actually pairs are here — asics / crocs / vans appear as site ids without their host in
    /// the same literal, so they are deliberately absent rather than guessed.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> Hosts =
        new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["cpcompany"] = "www.cpcompany.com",
            ["mjsfra"] = "www.marcjacobs.com",
            ["StoneNA"] = "www.stoneisland.com",
        };

    /// <summary>
    /// The URL shape the image spells out end to end, verbatim:
    /// <code>
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Product-Variation?pid=
    /// https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/
    /// https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit
    /// </code>
    /// The locale segment is <c>default</c> on some stores and <c>en_US</c> on others, so it is a
    /// parameter rather than a constant.
    /// </summary>
    public static string SitePath(string host, string site, string locale, string controller) =>
        $"https://{host}/on/demandware.store/Sites-{site}-Site/{locale}/{controller}";

    /// <summary><c>SitePath</c> with the locale left out, as the cpcompany template does.</summary>
    public static string SiteRoot(string host, string site) =>
        $"https://{host}/on/demandware.store/Sites-{site}-Site/";
'''

anchor = "    /// <summary>True when <paramref name=\"controller\"/> is one of the confirmed names.</summary>"
if anchor not in t:
    raise SystemExit("IsKnown anchor missing")
t = t.replace(anchor, extra.strip() + "\n\n" + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("DemandwareControllers: +2 raffle controllers, host map, site path helpers")
