import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\NikeFlow.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    /// <summary>\n    /// The marketplaces the binary supports")
end = t.find("    private const string Language = \"en\";")
if start < 0 or end < 0 or end <= start:
    raise SystemExit("country block: %d .. %d" % (start, end))

block = '''    /// <summary>
    /// The marketplaces the binary supports: <b>forty-two</b>.
    ///
    /// <para>
    /// R89 read them out of the image with <c>find_regex "Nike [A-Z]{2}$"</c> — one string per
    /// market, alphabetically ordered, 0x28 bytes apart. The earlier note in NIKE_PARITY said
    /// twenty-two; that was a window of this table, not the table. Twenty markets were missing and
    /// one of them was GB.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> Countries = new[]
    {
        "AT", "AU", "BE", "BG", "CA", "CH", "CZ", "DE", "DK", "ES", "FI",
        "FR", "GB", "GR", "GS", "HR", "HU", "IE", "IL", "IN", "IT", "JP",
        "LU", "MX", "MY", "NL", "NO", "NZ", "PH", "PL", "PT", "RO", "SE",
        "SG", "SI", "SK", "TH", "TR", "TW", "US", "VN", "ZA",
    };

    /// <summary>
    /// The country for this flow instance.
    ///
    /// <para>
    /// R86: this was <c>const string Marketplace = "US"</c> — one hardcoded market in a build that
    /// ships forty-two, while the binary carries the choice in an <b>instance</b> field
    /// (<c>_countryCode</c>). A constant cannot be per-task, so the flow could only ever check out in
    /// the United States no matter what the profile said.
    /// </para>
    /// </summary>
    public string CountryCode { get; set; } = "US";

    /// <summary>
    /// Maps a profile's ISO country onto a supported marketplace: an exact match if the binary
    /// supports it, otherwise US. Accepts a lowercase code, and treats "UK" as GB — the binary does
    /// have a GB market, so the alias resolves to something real rather than falling back.
    /// </summary>
    public static string CountryFor(string? profileCountry)
    {
        if (string.IsNullOrWhiteSpace(profileCountry)) return "US";

        var code = profileCountry.Trim().ToUpperInvariant();
        if (code == "UK") code = "GB";

        return Countries.Contains(code) ? code : "US";
    }

'''

t = t[:start] + block + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("Nike countries: 42, GB present, UK aliases to GB")
