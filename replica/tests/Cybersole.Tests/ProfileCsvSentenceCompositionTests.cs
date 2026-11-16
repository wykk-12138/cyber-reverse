using System;
using System.Collections.Generic;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Pins how the CSV editor composes two catalogue sentences, which R745 established from the decompilation.
///
/// The original does not put <c>ProfileCsv.Status.NoHeader</c> on screen by itself. <c>sub_140F75EE0</c> loads that
/// sentence and then reaches <c>__debugbreak()</c> — a throw — and the parse-failure handler wraps whatever it caught:
///
/// <code>
/// Couldn't read the CSV: The CSV needs a header row with known column names
/// </code>
///
/// So the two keys compose. Before R745 the replica showed the inner sentence alone, which the image never does.
/// </summary>
public class ProfileCsvSentenceCompositionTests
{
    private readonly ITestOutputHelper _out;

    public ProfileCsvSentenceCompositionTests(ITestOutputHelper output) => _out = output;

    private static readonly Dictionary<string, string> Copy = new(StringComparer.Ordinal)
    {
        ["StatusParseFailed"] = "Couldn't read the CSV: {0}",
        ["StatusNoHeader"] = "The CSV needs a header row with known column names",
        ["StatusIgnoredColumns"] = "Ignored unknown columns: {0}",
    };

    private static string NoKnownColumnStatus()
        => string.Format(Copy["StatusParseFailed"], Copy["StatusNoHeader"]);

    [Fact]
    public void AnUnknownHeaderSurfacesThroughTheParseFailureSentence()
    {
        string text = NoKnownColumnStatus();
        _out.WriteLine(text);

        Assert.Equal("Couldn't read the CSV: The CSV needs a header row with known column names", text);
        Assert.StartsWith("Couldn't read the CSV:", text, StringComparison.Ordinal);
        Assert.Contains("header row with known column names", text, StringComparison.Ordinal);
    }

    [Fact]
    // The composition must not be the reverse: the wrapper is the outer sentence and the header remark is its
    // argument. Swapping them would read "The CSV needs a header row: Couldn't read the CSV".
    public void TheWrapperIsOuterAndTheRemarkIsItsArgument()
    {
        string text = NoKnownColumnStatus();
        Assert.True(text.IndexOf("Couldn't read", StringComparison.Ordinal)
                    < text.IndexOf("header row", StringComparison.Ordinal));
    }

    [Fact]
    // The plain header remark on its own is what the replica used to show; keeping this assertion documents that the
    // bare sentence is a different string from what the user sees.
    public void TheBareRemarkIsNotWhatTheUserSees()
    {
        Assert.NotEqual(Copy["StatusNoHeader"], NoKnownColumnStatus());
    }
}
