using Cybersole.Services.Localization;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The four dictionaries must be embedded, complete, and actually translated.
///
/// Round 126 concluded the original only localised four strings. Round 131 proved that wrong:
/// each resource carries 1142 keys. These tests hold the corrected finding down — a regression
/// that dropped a dictionary, or that shipped four copies of English, would fail here.
///
/// What this file does NOT catch, and why a second test exists:
///
///   R168 found en and ja each held 1143 properties — `Solver.AllCaptchas` appeared twice with
///   the same value. Every assertion here stayed green, because `LocalizationService.For` returns
///   a Dictionary and a Dictionary collapses duplicate keys on the way in. `dictionary.Count` was
///   1142 and correct; the file was 1143 and wrong.
///
///   ParityDocTests.EveryLocaleDictionaryHasTheSameKeyCount enumerates properties instead of
///   counting dictionary entries, so it sees the duplicate. Neither test subsumes the other:
///   a duplicate makes this file green and that one red, a deletion makes both red.
///
///   Two mutations back the pair — `round 168 -- a locale dictionary repeats a key` and
///   `round 169 -- a locale dictionary loses a key`.
/// </summary>
public class LocaleDictionaryTests
{
    private readonly ITestOutputHelper _out;
    public LocaleDictionaryTests(ITestOutputHelper output) => _out = output;

    private const int ExpectedKeys = 1142;

    [Fact]
    public void AllFourResourcesAreEmbedded()
    {
        var found = LocalizationService.AvailableResources().OrderBy(x => x).ToList();
        _out.WriteLine("embedded: " + string.Join(", ", found));

        Assert.Equal(4, found.Count);
        foreach (var (_, resource, _) in LocalizationService.Languages)
            Assert.Contains(resource, found);
    }

    [Fact]
    public void EveryDictionaryHasTheSameKeyCount()
    {
        foreach (var (tag, _, display) in LocalizationService.Languages)
        {
            var dictionary = LocalizationService.For(tag);
            _out.WriteLine($"{tag,-8} {display,-22} {dictionary.Count} keys");
            Assert.Equal(ExpectedKeys, dictionary.Count);
        }
    }

    [Fact]
    public void EveryDictionaryCoversTheSameKeys()
    {
        var english = LocalizationService.For("en").Keys.ToHashSet();
        foreach (var (tag, _, _) in LocalizationService.Languages)
        {
            var keys = LocalizationService.For(tag).Keys.ToHashSet();
            var missing = english.Except(keys).ToList();
            var extra = keys.Except(english).ToList();

            _out.WriteLine($"{tag,-8} missing={missing.Count} extra={extra.Count}");
            Assert.Empty(missing);
            Assert.Empty(extra);
        }
    }

    [Fact]
    public void TranslationsDifferFromEnglish()
    {
        // four copies of the English file would satisfy every check above; this is what catches it
        var samples = new[] { "Common.Save", "Common.Cancel", "Common.Delete" };

        foreach (var (tag, _, display) in LocalizationService.Languages)
        {
            var dictionary = LocalizationService.For(tag);
            var rendered = samples.Select(k => dictionary.TryGetValue(k, out var v) ? v : "?").ToList();
            _out.WriteLine($"{tag,-8} {display,-22} " + string.Join(" / ", rendered));

            if (tag == "en") continue;

            var differs = samples.Any(k =>
                dictionary.TryGetValue(k, out var v)
                && LocalizationService.For("en").TryGetValue(k, out var e)
                && v != e);
            Assert.True(differs, $"{tag} looks like a copy of English");
        }
    }

    [Fact]
    public void ScriptIsCorrectForEachLanguage()
    {
        // the presence of the right script is a stronger check than "not equal to English"
        Assert.Matches(@"[\u3040-\u30ff\u4e00-\u9fff]", LocalizationService.Translate("ja", "Common.Save"));
        Assert.Matches(@"[\uac00-\ud7af]", LocalizationService.Translate("ko", "Common.Save"));
        Assert.Matches(@"[\u4e00-\u9fff]", LocalizationService.Translate("zh-Hans", "Common.Save"));

        _out.WriteLine("ja: " + LocalizationService.Translate("ja", "Common.Save"));
        _out.WriteLine("ko: " + LocalizationService.Translate("ko", "Common.Save"));
        _out.WriteLine("zh: " + LocalizationService.Translate("zh-Hans", "Common.Save"));
    }

    [Fact]
    public void UnknownKeyFallsBackToItself()
    {
        // a missing string must render as the key, never as blank — a blank label reads as a bug
        Assert.Equal("No.Such.Key", LocalizationService.Translate("ja", "No.Such.Key"));
        Assert.Equal(string.Empty, LocalizationService.Translate("ja", ""));
    }

    [Theory]
    [InlineData("English", "en")]
    [InlineData("Japanese", "ja")]
    [InlineData("Korean", "ko")]
    [InlineData("Chinese (Simplified)", "zh-Hans")]
    [InlineData("ChineseSimplified", "zh-Hans")]
    [InlineData("en", "en")]
    [InlineData("zh-Hans", "zh-Hans")]
    [InlineData(null, "en")]
    [InlineData("Klingon", "en")]
    public void TagResolutionAcceptsEveryStoredForm(string? stored, string expected)
        => Assert.Equal(expected, LocalizationService.ResolveTag(stored));
}
