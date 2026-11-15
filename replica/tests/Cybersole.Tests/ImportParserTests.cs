using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class ImportParserTests
{
    [Theory]
    [InlineData("a@b.c:pass")]
    [InlineData("a@b.c,pass")]
    [InlineData("a@b.c|pass")]
    public void ParseAccounts_Accepts_All_Separators(string line)
    {
        var parsed = ImportParser.ParseAccounts(line);
        Assert.Single(parsed);
        Assert.Equal("a@b.c", parsed[0].Email);
        Assert.Equal("pass", parsed[0].Password);
    }

    [Fact]
    public void ParseAccounts_Skips_Invalid_And_Comment_Lines()
    {
        var text = """
                   # comment
                   a@b.c:pass
                   not-an-email:pass
                   d@e.f
                   g@h.i:pw
                   """;
        var parsed = ImportParser.ParseAccounts(text);
        Assert.Equal(2, parsed.Count);
        Assert.Equal("a@b.c", parsed[0].Email);
        Assert.Equal("g@h.i", parsed[1].Email);
    }

    [Fact]
    public void ParseAccounts_Handles_Password_With_Colon()
    {
        var parsed = ImportParser.ParseAccounts("a@b.c:pa:ss:word");
        Assert.Single(parsed);
        Assert.Equal("pa:ss:word", parsed[0].Password);
    }

    [Fact]
    public void ParseAccounts_Empty_Input_Returns_Empty()
    {
        Assert.Empty(ImportParser.ParseAccounts(null));
        Assert.Empty(ImportParser.ParseAccounts("   "));
    }

    [Fact]
    public void ParseProxies_Handles_All_Formats()
    {
        var text = """
                   1.2.3.4:8080
                   1.2.3.4:8080:user:pass
                   socks5://u:p@5.6.7.8:1080
                   # skip me
                   invalid
                   """;
        var parsed = ImportParser.ParseProxies(text);
        Assert.Equal(3, parsed.Count);
        Assert.Equal("1.2.3.4", parsed[0].Host);
        Assert.Equal(8080, parsed[0].Port);
        Assert.Equal("user", parsed[1].Username);
        Assert.Equal("socks5", parsed[2].Scheme);
    }

    [Fact]
    public void ParseSizes_Splits_And_Deduplicates()
    {
        var sizes = ImportParser.ParseSizes("9, 10; 10.5  10");
        Assert.Equal(new[] { "9", "10", "10.5" }, sizes);
    }

    [Fact]
    public void ParseSizes_Empty_Returns_Empty()
    {
        Assert.Empty(ImportParser.ParseSizes(""));
        Assert.Empty(ImportParser.ParseSizes(null));
    }
}
