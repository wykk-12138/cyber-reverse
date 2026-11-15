import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\NikeMarketplaceTests.cs"
t = io.open(p, encoding="utf-8").read()

# The list is forty-two, not twenty-two: R86 read a window of the table and missed twenty.
t = t.replace('''/// The binary's string table spells out twenty-two markets as "Nike XX" entries, and its
/// <c>_countryCode</c> is an <b>instance</b> field — one per flow, chosen by the task. The replica
/// had <c>const string Marketplace = "US"</c>, which cannot be per-task: every checkout went to the
/// United States no matter what the profile said.
/// </para>
///
/// <code>
/// IT JP LU MX MY NL NO NZ PH PL PT RO SE SG SI SK TH TR TW US VN ZA
/// </code>''',
'''/// The binary's string table spells out <b>forty-two</b> markets as "Nike XX" entries, and its
/// <c>_countryCode</c> is an <b>instance</b> field — one per flow, chosen by the task. The replica
/// had <c>const string Marketplace = "US"</c>, which cannot be per-task: every checkout went to the
/// United States no matter what the profile said.
/// </para>
///
/// <code>
/// AT AU BE BG CA CH CZ DE DK ES FI FR GB GR GS HR HU IE IL IN IT JP LU MX MY NL NO NZ PH PL PT RO
/// SE SG SI SK TH TR TW US VN ZA
/// </code>
///
/// <para>
/// R86 read twenty-two of them — a window, not the table — and so claimed the binary had no GB
/// market. R89 read the table: forty-two entries, GB included.''')

t = t.replace('''    /// <summary>The twenty-two marketplaces, in the binary's order.</summary>
    [Fact]
    public void TheBinaryHasTwentyTwoMarkets()
    {
        _out.WriteLine(string.Join(" ", NikeFlow.Countries));

        Assert.Equal(22, NikeFlow.Countries.Count);
        Assert.Equal(22, NikeFlow.Countries.Distinct().Count());
        Assert.Equal("IT", NikeFlow.Countries[0]);
        Assert.Equal("US", NikeFlow.Countries[19]);
        Assert.Equal("ZA", NikeFlow.Countries[^1]);
    }''',
'''    /// <summary>The forty-two marketplaces, in the binary's (alphabetical) order.</summary>
    [Fact]
    public void TheBinaryHasFortyTwoMarkets()
    {
        _out.WriteLine(string.Join(" ", NikeFlow.Countries));

        Assert.Equal(42, NikeFlow.Countries.Count);
        Assert.Equal(42, NikeFlow.Countries.Distinct().Count());
        Assert.Equal("AT", NikeFlow.Countries[0]);
        Assert.Equal("GB", NikeFlow.Countries[12]);
        Assert.Equal("ZA", NikeFlow.Countries[^1]);

        // alphabetically ordered, the way the image stores them
        Assert.Equal(NikeFlow.Countries.OrderBy(c => c, StringComparer.Ordinal), NikeFlow.Countries);
    }''')

t = t.replace('''    [InlineData("UK", "US")]   // the binary has no GB market; UK is not silently invented''',
              '''    [InlineData("UK", "GB")]   // the alias resolves onto a market the binary really has
    [InlineData("GB", "GB")]''')

t = t.replace('''    [InlineData("DE", "US")]
    [InlineData("CN", "US")]''',
              '''    [InlineData("DE", "DE")]   // Germany is in the table
    [InlineData("FR", "FR")]
    [InlineData("CN", "US")]   // China is not''')

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("marketplace tests updated to 42")
