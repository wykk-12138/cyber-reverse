using Xunit;
using Cybersole.Ui.Views.Profiles;

namespace Cybersole.Tests;

/// <summary>
/// R256: the CSV paste editor's row parser. It is a pure function, so it can be pinned here instead of only through the
/// window — and it is the piece that decides how many profiles a paste will create.
/// </summary>
public sealed class ProfileCsvParseTests
{
    [Fact]
    public void AHeaderLineIsSkippedAndBlankLinesAreIgnored()
    {
        var rows = ProfileCsvEditorView.Parse("email,firstName\n\na@b.c,Ada\n\nd@e.f,Dan\n");

        Assert.Equal(2, rows.Count);
        Assert.Equal(new[] { "a@b.c", "Ada" }, rows[0]);
        Assert.Equal(new[] { "d@e.f", "Dan" }, rows[1]);
    }

    [Fact]
    public void WithoutAHeaderEveryLineIsAProfile()
    {
        var rows = ProfileCsvEditorView.Parse("a@b.c,Ada\nd@e.f,Dan");

        Assert.Equal(2, rows.Count);
    }

    [Fact]
    public void EmptyTextParsesToNothing()
    {
        Assert.Empty(ProfileCsvEditorView.Parse(""));
        Assert.Empty(ProfileCsvEditorView.Parse("   \n\n  "));
    }
}
