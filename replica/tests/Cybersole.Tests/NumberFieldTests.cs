using System;
using Cybersole.Ui.Views;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Pins the number field's display and read-back, which R755 found out of step with the live window.
///
/// The original shows "2,500" in the Default Monitor and Default Error fields — that string is what its accessibility
/// tree reports, not a guess. Formatting the replica's field the same way is only half the change: every reader has to
/// accept the separator too, or the field would display a value it cannot parse back and the caller would keep the old
/// one without telling anyone.
/// </summary>
public class NumberFieldTests
{
    private readonly ITestOutputHelper _out;

    public NumberFieldTests(ITestOutputHelper output) => _out = output;

    [Theory]
    [InlineData(2500, "2,500")]
    [InlineData(10, "10")]
    [InlineData(0, "0")]
    [InlineData(1234567, "1,234,567")]
    // R755 measured "2500" and "10" on the live Default Monitor / Default Timeout fields; the thousands separator
    // appears from four digits, and nothing below a thousand gains one.
    public void TheFieldFormatsWithThousandsSeparators(int value, string expected)
    {
        var box = UiKit.Number(value);
        _out.WriteLine(box.Text ?? string.Empty);
        Assert.Equal(expected, box.Text);
    }

    [Theory]
    [InlineData("2,500", 2500)]
    [InlineData("2500", 2500)]
    [InlineData("1,234,567", 1234567)]
    [InlineData("10", 10)]
    [InlineData(" 2,500 ", 2500)]
    // The reader tolerates both spellings, so a value typed without separators still saves.
    public void TheReaderAcceptsEitherSpelling(string text, int expected)
    {
        Assert.True(UiKit.TryReadInt(text, out var value));
        Assert.Equal(expected, value);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("abc")]
    [InlineData(null)]
    public void AnEmptyOrUnparseableFieldIsRejectedRatherThanReadAsZero(string? text)
    {
        Assert.False(UiKit.TryReadInt(text, out _));
    }

    [Fact]
    // The round trip is the point: what the field displays must read back as the value it was given.
    public void TheFieldRoundTripsWhateverItDisplays()
    {
        foreach (var expected in new[] { 0, 1, 999, 2500, 12_345, 999_999, 1_000_000 })
        {
            var box = UiKit.Number(expected);
            Assert.True(UiKit.TryReadInt(box.Text, out var read), "failed to read " + box.Text);
            Assert.Equal(expected, read);
        }
    }
}
