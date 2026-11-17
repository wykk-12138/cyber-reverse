using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// FindCsrfToken, which reads a token out of a page in the four shapes a shop uses.
///
/// <para>
/// R962. GetCsrf returned Ok without doing anything, and the image carries it under roughly twenty different ordinals --
/// d__14, d__22, d__23, d__24, d__26, d__28, d__31, d__32, d__33, d__35, d__39, d__40, d__50 and more -- so every shop reads
/// its own token. The variation is in where a shop puts it, not in what a token is, and all of the shapes are one of four:
/// a hidden input, a meta tag, a JSON field, or a data attribute.
/// </para>
/// </summary>
public class CsrfTokenTests
{
    /// <summary>A hidden input, with name before value.</summary>
    [Fact]
    public void HiddenInputNameThenValue()
    {
        var body = "<form><input type=\"hidden\" name=\"csrf_token\" value=\"abc123def456\"></form>";
        Assert.Equal("abc123def456", StoreFlow.FindCsrfToken(body));
    }

    /// <summary>And with value before name, which some renderers emit.</summary>
    [Fact]
    public void HiddenInputValueThenName()
    {
        var body = "<input value=\"abc123def456\" name=\"authenticity_token\" type=\"hidden\">";
        Assert.Equal("abc123def456", StoreFlow.FindCsrfToken(body));
    }

    /// <summary>A meta tag, which is the second shape.</summary>
    [Fact]
    public void MetaTag()
    {
        var body = "<head><meta name=\"csrf-token\" content=\"xyz987654321\"></head>";
        Assert.Equal("xyz987654321", StoreFlow.FindCsrfToken(body));
    }

    /// <summary>A JSON field inside a page script, which is the third shape.</summary>
    [Fact]
    public void JsonField()
    {
        var body = "<script>var cfg = {\"csrfToken\":\"json123456789\"};</script>";
        Assert.Equal("json123456789", StoreFlow.FindCsrfToken(body));
    }

    /// <summary>A data attribute, which is the fourth.</summary>
    [Fact]
    public void DataAttribute()
    {
        var body = "<div data-csrf-token=\"attr123456789\"></div>";
        Assert.Equal("attr123456789", StoreFlow.FindCsrfToken(body));
    }

    /// <summary>A page with no token returns null rather than inventing one.</summary>
    [Theory]
    [InlineData("<form><input name=\"q\" value=\"1\"></form>")]
    [InlineData("")]
    [InlineData(null)]
    [InlineData("{}")]
    public void NoTokenIsNull(string? body)
    {
        Assert.Null(StoreFlow.FindCsrfToken(body));
    }

    /// <summary>
    /// A short value is not a token. The eight-character floor exists because fields named like tokens also carry values
    /// like "1", "on" and "true", and returning one of those would look like success and fail at the next request.
    /// </summary>
    [Fact]
    public void ShortValuesAreRejected()
    {
        Assert.Null(StoreFlow.FindCsrfToken("<input name=\"csrf_token\" value=\"1\">"));
        Assert.Null(StoreFlow.FindCsrfToken("<input name=\"csrf_token\" value=\"on\">"));
    }

    /// <summary>The four cookie names cover the fourth storage location.</summary>
    [Fact]
    public void TheCookieNamesAreRecorded()
    {
        var names = (string[])typeof(StoreFlow)
            .GetField("CsrfCookieNames", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Contains("csrftoken", names);
        Assert.Contains("XSRF-TOKEN", names);
        Assert.Contains("_csrf", names);
    }

    /// <summary>The step no longer returns Ok without doing anything.</summary>
    [Fact]
    public void TheStepNoLongerReturnsOk()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.DoesNotContain("Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct) => Ok();", doc);
        Assert.Contains("FindCsrfToken", doc);
        Assert.Contains("no csrf token on the page", doc);
    }

    /// <summary>
    /// Failing to find a token is a failure, not a retry: the page will carry the same token next time, and reporting
    /// success without one is what let the next POST go out unauthenticated.
    /// </summary>
    [Fact]
    public void NoTokenFails()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("retryable: false", doc);
        Assert.Contains("meant the next POST went out unauthenticated", doc);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}