using System;
using System.Collections.Generic;
using Cybersole.Core.Reporting;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for <see cref="SizePresetDeletePrompt"/>, which reimplements the text half of
/// <c>sub_140641190</c>.
///
/// The templates are the shipped catalogue's, including its inconsistency: the title says "presets" and the message
/// says "sizes". That is a quirk to keep, not to tidy — a replica that harmonised them would differ from the original
/// in a string the user reads.
/// </summary>
public class SizePresetDeletePromptTests
{
    private readonly ITestOutputHelper _out;

    public SizePresetDeletePromptTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["Settings.Sizes.DeleteConfirm.TitleFormat"] = "Delete {0} presets?",
        ["Settings.Sizes.DeleteConfirm.MessageFormat"] =
            "Are you sure you want to delete {0} sizes?\nYou cannot undo this action.",
    };

    private static (string Title, string Message)? For(int count)
        => SizePresetDeletePrompt.For(count, k => Copy[k]);

    [Fact]
    // The decompiled guard skips everything when the count is zero, so no dialog exists to describe.
    public void AnEmptySelectionProducesNoConfirmation()
    {
        Assert.Null(For(0));
    }

    [Theory]
    [InlineData(1)]
    [InlineData(2)]
    [InlineData(48)]
    public void ANonEmptySelectionNamesTheCountInBothTexts(int count)
    {
        var pair = For(count);
        Assert.NotNull(pair);
        _out.WriteLine(pair!.Value.Title);
        _out.WriteLine(pair.Value.Message);

        Assert.Equal("Delete " + count + " presets?", pair.Value.Title);
        Assert.StartsWith("Are you sure you want to delete " + count + " sizes?", pair.Value.Message,
            StringComparison.Ordinal);
        Assert.EndsWith("You cannot undo this action.", pair.Value.Message, StringComparison.Ordinal);
    }

    [Fact]
    // Preserved verbatim, not corrected: title says "presets", message says "sizes".
    public void TheShippedWordingIsKeptEvenWhereItDisagreesWithItself()
    {
        var pair = For(3);
        Assert.Contains("presets", pair!.Value.Title, StringComparison.Ordinal);
        Assert.DoesNotContain("presets", pair.Value.Message, StringComparison.Ordinal);
        Assert.Contains("sizes", pair.Value.Message, StringComparison.Ordinal);
    }

    [Fact]
    // One count feeds both texts; they cannot disagree about it.
    public void BothTextsCarryTheSameCount()
    {
        var pair = For(7);
        Assert.Contains("7", pair!.Value.Title, StringComparison.Ordinal);
        Assert.Contains("7", pair.Value.Message, StringComparison.Ordinal);
    }
}
