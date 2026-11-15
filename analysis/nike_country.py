import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\NikeFlow.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    private const string Marketplace = "US";
    private const string Language = "en";'''
new = '''    /// <summary>
    /// The marketplaces the binary supports: twenty-two, spelled out as "Nike XX" entries in its
    /// string table (round 50). The order is the binary's.
    /// </summary>
    public static readonly IReadOnlyList<string> Countries = new[]
    {
        "IT", "JP", "LU", "MX", "MY", "NL", "NO", "NZ",
        "PH", "PL", "PT", "RO", "SE", "SG", "SI", "SK",
        "TH", "TR", "TW", "US", "VN", "ZA",
    };

    /// <summary>
    /// The country for this flow instance.
    ///
    /// <para>
    /// R86: this was <c>const string Marketplace = "US"</c> — one hardcoded market in a build that
    /// ships twenty-two, while the binary carries the choice in an <b>instance</b> field
    /// (<c>_countryCode</c>). A constant cannot be per-task, so the flow could only ever check out in
    /// the United States no matter what the profile said.
    /// </para>
    /// </summary>
    public string CountryCode { get; set; } = "US";

    /// <summary>
    /// Maps a profile's ISO country onto a supported marketplace: an exact match if the binary
    /// supports it, otherwise US. Also accepts a lowercase code and a "UK" alias for GB, which is
    /// what profiles written by hand tend to contain.
    /// </summary>
    public static string CountryFor(string? profileCountry)
    {
        if (string.IsNullOrWhiteSpace(profileCountry)) return "US";

        var code = profileCountry.Trim().ToUpperInvariant();
        if (code == "UK") code = "GB";

        return Countries.Contains(code) ? code : "US";
    }

    private const string Language = "en";'''
if old not in t:
    raise SystemExit("marketplace const anchor missing")
t = t.replace(old, new, 1)

# The two use sites become instance reads.
t = t.replace('$"?filter=marketplace({Marketplace})&filter=language({Language})"',
              '$"?filter=marketplace({CountryCode})&filter=language({Language})"', 1)
t = t.replace('$"https://api.nike.com/buy/carts/v2/{Marketplace}/Nike/SNKRS?format=simplified"',
              '$"https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified"', 1)

if "Marketplace" in t:
    # print the remaining mentions so the report is honest
    for i, line in enumerate(t.split("\n"), 1):
        if "Marketplace" in line:
            print("remaining mention", i, line.strip()[:100])

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("NikeFlow: country is per-instance, 22 markets")
