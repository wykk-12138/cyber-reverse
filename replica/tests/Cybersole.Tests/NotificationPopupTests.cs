using Cybersole.Ui.Views.Common;
using Cybersole.Ui.Views.Modals;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R336: the notification popup, read off the running build.
///
/// <para>
/// The live panel is a header reading "0 Notifications" beside one Clear button, then the shared "Nothing to see here"
/// headline with "Your notifications will show up here" under it. The replica had a window titled just "Notifications"
/// with a Clock row and a Delete button — neither of which is in the live panel's tree — so both were removed and the
/// empty state was made verbatim. The tests below can only pin the strings and the shape; the panel is a Window, so
/// there is no layout to assert without a host.
/// </para>
/// </summary>
public sealed class NotificationPopupTests
{
    private readonly ITestOutputHelper _out;
    public NotificationPopupTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheEmptyStateIsTheHeadlinePlusTheLiveSecondLine()
    {
        _out.WriteLine(NotificationView.EmptyBody);
        Assert.Equal("Your notifications will show up here", NotificationView.EmptyBody);
        Assert.Equal("Nothing to see here", EmptyView.Headline);
    }
}
