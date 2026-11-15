using System.Linq;
using Cybersole.Ui.Views.Modals;
using Cybersole.Ui.Views.Profiles;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R357: two more bound fields that the image names and the replica did not expose.
///
/// <para>
/// <c>MessageBoxDialog</c> binds ActionText / CancelText / ShowAction / ShowCancel / Type; the fourth of those had no
/// member. <c>ProfileCsvEditorView</c> binds GroupName next to ColumnChoices / ProfileCount, and the editor already had the
/// group combo — it just never exposed what was chosen.
/// </para>
/// </summary>
public sealed class DialogFieldTests
{
    private readonly ITestOutputHelper _out;
    public DialogFieldTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheMessageBoxCarriesAType()
    {
        var type = typeof(MessageBoxDialog);
        var prop = type.GetProperty("Type");

        // a Window cannot be constructed without an Avalonia platform, so this is a reflection assertion
        _out.WriteLine("Type property: " + prop?.PropertyType.Name);
        Assert.NotNull(prop);
        Assert.Equal("MessageBoxType", prop!.PropertyType.Name);
    }

    [Fact]
    public void TheCsvEditorExposesTheChosenGroup()
    {
        using var services = TestServices.Create();
        var editor = new ProfileCsvEditorView(services);

        _out.WriteLine("group: '" + editor.GroupName + "'");
        Assert.NotNull(editor.GroupName);
    }
}
