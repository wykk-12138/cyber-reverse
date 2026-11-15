using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;

namespace Cybersole.Ui.Views.Settings.Modals;

/// <summary>
/// Base for the Settings creator/edit dialogs
/// (Cybersole.Ui.Views.Settings.Modals.* — ten separate XAML files in the original).
/// Each one is a small Window with a title, a body and a Close / Save footer.
/// </summary>
public abstract class SettingsModal : Window
{
    private readonly TextBlock _status = UiKit.Status();

    protected SettingsModal(string title, double width = 520, double height = 460)
    {
        Title = title;
        Width = width;
        Height = height;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        Body = new StackPanel { Spacing = 6 };
        Footer = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Margin = new Thickness(0, 12, 0, 0),
        };

        var root = new StackPanel { Spacing = 6, Margin = new Thickness(16) };
        root.Children.Add(UiKit.Title(title));
        root.Children.Add(UiKit.Scroll(Body));
        root.Children.Add(Footer);
        root.Children.Add(_status);

        Content = root;
    }

    /// <summary>Dialog body — subclasses add rows here.</summary>
    protected StackPanel Body { get; }

    /// <summary>Dialog footer — subclasses add buttons here.</summary>
    protected StackPanel Footer { get; }

    protected void SetStatus(string text) => _status.Text = text;

    /// <summary>The recovered <c>Close</c> command present on every modal.</summary>
    protected Button CloseButton() => UiKit.Button("Close", Close);

    /// <summary>The recovered <c>Save</c> command present on every modal.</summary>
    protected Button SaveButton(Action onSave) => UiKit.Button("Save", () =>
    {
        try
        {
            onSave();
            Close();
        }
        catch (Exception ex)
        {
            SetStatus(ex.Message);
        }
    });

    /// <summary>The recovered <c>Delete</c> command (captcha / solver / size modals).</summary>
    protected Button DeleteButton(Action onDelete) => UiKit.Button("Delete", () =>
    {
        try
        {
            onDelete();
            Close();
        }
        catch (Exception ex)
        {
            SetStatus(ex.Message);
        }
    });

    /// <summary>Build the footer from the given buttons, always appending Close.</summary>
    protected void BuildFooter(params Button[] actions)
    {
        foreach (var b in actions) Footer.Children.Add(b);
        Footer.Children.Add(CloseButton());
    }
}
