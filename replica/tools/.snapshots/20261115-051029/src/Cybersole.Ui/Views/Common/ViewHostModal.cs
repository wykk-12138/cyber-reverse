using Avalonia.Controls;
using Cybersole.Services;

namespace Cybersole.Ui.Views.Common;

/// <summary>
/// Hosts an existing <see cref="UserControl"/> in a modal window.
///
/// R181: ProfileViews' "Open CSV editor" and "Create group" buttons wrote status text saying
/// "No CSV editor window exists yet" and "No group editor window exists yet" — while
/// ProfileCsvEditorView and ProfileGroupView sat in the same file, complete, as UserControls.
/// The views were never missing; nothing put them on screen.
///
/// This is the missing piece and nothing more: it does not build a body, it adopts one. The
/// alternative — giving each view its own Window subclass — duplicates the title/close/scroll
/// chrome that SettingsModal already provides.
/// </summary>
public sealed class ViewHostModal : Settings.Modals.SettingsModal
{
    public ViewHostModal(string title, Control content, double width = 760, double height = 560,
        params Button[] actions)
        : base(title, width, height)
    {
        // The hosted control scrolls itself; wrapping it in Body's ScrollViewer would nest two
        // scroll regions, and the inner one would never get the wheel.
        Body.Children.Add(content);

        // R61: a hosted view that has to confirm something ("Move to which group?") needs a
        // button in the footer, not just Close. Passing none keeps the round-181 behaviour.
        if (actions.Length == 0) BuildFooter();
        else BuildFooter(actions);
    }

    /// <summary>
    /// Opens <paramref name="content"/> modally and reports whether an owner window existed.
    /// Returns false without throwing when the control is not attached to a window yet — the
    /// same guard <c>ProfileViews.OpenProfileEditor</c> uses, for the same reason: during a
    /// rebuild there is no TopLevel, and throwing there would take down the page.
    /// </summary>
    public static bool Show(Control owner, string title, Control content,
        double width = 760, double height = 560, params Button[] actions)
    {
        if (TopLevel.GetTopLevel(owner) is not Window window) return false;

        var modal = new ViewHostModal(title, content, width, height, actions);
        _ = modal.ShowDialog(window);
        return true;
    }
}
