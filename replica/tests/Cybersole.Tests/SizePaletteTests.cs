using Cybersole.Core.Models;
using Xunit;

namespace Cybersole.Tests;

public class SizePaletteTests
{
    [Fact]
    public void Standard_Ladder_Is_Twenty_Sizes()
        => Assert.Equal(20, SizePalette.Standard.Count);

    [Fact]
    public void Custom_Sizes_Are_Appended()
    {
        var palette = SizePalette.Build(new[] { "15", "16" });
        Assert.Equal("15", palette[^2]);
        Assert.Equal("16", palette[^1]);
    }

    [Fact]
    public void Duplicates_Are_Removed_Case_Insensitive()
    {
        var palette = SizePalette.Build(new[] { "10", "10.0", "10" });
        Assert.Single(palette.Where(s => s == "10"));
        Assert.Equal(20, palette.Count);
    }

    [Fact]
    public void Trailing_Point_Zero_Is_Normalised()
        => Assert.Equal("10", SizePalette.Normalise("10.0"));

    [Fact]
    public void Blank_Entries_Are_Skipped()
    {
        var palette = SizePalette.Build(new[] { "", "  ", "11.5" });
        Assert.Equal(20, palette.Count);      // 11.5 already standard
    }

    [Fact]
    public void Null_List_Returns_Standard_Only()
        => Assert.Equal(SizePalette.Standard, SizePalette.Build(null));

    [Theory]
    [InlineData("10", true)]
    [InlineData("10.5", true)]
    [InlineData("44 2/3", false)]
    [InlineData("abc", false)]
    [InlineData("", false)]
    [InlineData("12½", true)]
    public void Validity_Check_Rejects_Typos(string value, bool expected)
        => Assert.Equal(expected, SizePalette.IsValid(value));

    [Fact]
    public void Order_Is_Preserved()
    {
        var palette = SizePalette.Build(new[] { "16", "15", "17" });
        Assert.Equal(new[] { "16", "15", "17" }, palette.Skip(20).ToArray());
    }
}
