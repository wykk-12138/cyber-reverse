using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;

namespace Cybersole.Ui.Views;

/// <summary>
/// Declarative helpers for building Avalonia views in code. The original ships XAML; the
/// replica builds the same layouts directly so the whole UI stays compilable and testable
/// without a markup pass.
/// </summary>
public static class UiKit
{
    public static IBrush Dim { get; } = new SolidColorBrush(Color.FromArgb(0xB0, 0xC8, 0xC8, 0xC8));

    public static TextBlock Title(string text) => new()
    {
        Text = text,
        FontSize = 16,
        FontWeight = FontWeight.SemiBold,
        Margin = new Thickness(0, 0, 0, 8),
    };

    public static TextBlock Caption(string text) => new()
    {
        Text = text,
        Opacity = 0.72,
        FontSize = 12,
        TextWrapping = TextWrapping.Wrap,
        Margin = new Thickness(0, 0, 0, 8),
    };

    public static TextBlock Label(string text, double width = 210) => new()
    {
        Text = text,
        Width = width,
        VerticalAlignment = VerticalAlignment.Center,
    };

    public static TextBlock Status(string? text = null) => new()
    {
        Text = text ?? string.Empty,
        Opacity = 0.75,
        FontSize = 12,
        TextWrapping = TextWrapping.Wrap,
    };

    public static TextBox Text(string? value = null, string? watermark = null, double width = 240,
        bool password = false) => new()
    {
        Text = value ?? string.Empty,
        Watermark = watermark,
        Width = width,
        PasswordChar = password ? '*' : '\0',
    };

    public static TextBox Number(int? value, double width = 120) =>
        Text(value?.ToString(), "0", width);

    public static CheckBox Check(string text, bool value, Action<bool>? onChanged = null)    {
        var box = new CheckBox { Content = text, IsChecked = value };
        if (onChanged is not null)
            box.IsCheckedChanged += (_, _) => onChanged(box.IsChecked == true);
        return box;
    }

    public static Button Button(string text, Action onClick, double width = double.NaN)
    {
        var b = new Button { Content = text };
        if (!double.IsNaN(width)) b.Width = width;
        b.Click += (_, _) => onClick();
        return b;
    }

    public static ComboBox Combo(IEnumerable<string> items, int selected = 0,
        Action<int>? onChanged = null, double width = 240)
    {
        var combo = new ComboBox { ItemsSource = items.ToList(), Width = width };
        if (combo.ItemsSource is IList<string> list && selected >= 0 && selected < list.Count)
            combo.SelectedIndex = selected;
        if (onChanged is not null)
            combo.SelectionChanged += (_, _) => onChanged(combo.SelectedIndex);
        return combo;
    }

    /// <summary>One label/input pair in a two-column grid.</summary>
    public static Control Row(string label, Control input, double labelWidth = 210) =>
        TwoColumn(Label(label, labelWidth), input);

    /// <summary>
    /// A labelled checkbox, with the text on the label rather than on the box.
    /// </summary>
    /// <remarks>
    /// R67: four call sites wrote <c>UiKit.Row("Enable clock", UiKit.Check("Enable clock", v))</c>,
    /// which rendered the same sentence twice — once as the row label and again beside the tick.
    /// A screenshot showed it; nothing in the code looks wrong.
    ///
    /// The checkbox keeps empty Content: the row's label already says what it is.
    /// </remarks>
    public static Control RowCheck(string label, bool value,
        Action<bool>? onChanged = null, double labelWidth = 210) =>
        Row(label, Check(string.Empty, value, onChanged), labelWidth);

    public static Control TwoColumn(Control left, Control right)
    {
        var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,*") };
        Grid.SetColumn(left, 0);
        Grid.SetColumn(right, 1);
        right.Margin = new Thickness(8, 4, 0, 4);
        left.Margin = new Thickness(0, 4, 0, 4);
        grid.Children.Add(left);
        grid.Children.Add(right);
        return grid;
    }

    /// <summary>A vertical stack of rows.</summary>
    public static Control Form(params Control[] rows)
    {
        var stack = new StackPanel { Spacing = 6 };
        foreach (var r in rows) stack.Children.Add(r);
        return stack;
    }

    /// <summary>Horizontal button strip.</summary>
    public static Control Buttons(params Control[] buttons)
    {
        var stack = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Margin = new Thickness(0, 10, 0, 0),
        };
        foreach (var b in buttons) stack.Children.Add(b);
        return stack;
    }

    /// <summary>A titled card with padding and a border.</summary>
    public static Border Card(string title, Control content)
    {
        var stack = new StackPanel { Spacing = 6 };
        stack.Children.Add(Title(title));
        stack.Children.Add(content);

        return new Border
        {
            BorderThickness = new Thickness(1),
            BorderBrush = new SolidColorBrush(Color.FromArgb(0x28, 0xFF, 0xFF, 0xFF)),
            CornerRadius = new CornerRadius(6),
            Padding = new Thickness(12),
            Margin = new Thickness(0, 0, 0, 12),
            Child = stack,
        };
    }

    /// <summary>A card whose body is an arbitrary set of controls stacked vertically.</summary>
    public static Border Section(string title, params Control[] children)
    {
        var stack = new StackPanel { Spacing = 6 };
        foreach (var c in children) stack.Children.Add(c);
        return Card(title, stack);
    }

    /// <summary>
    /// A page header: the large title over its one-line subtitle, as every Settings page prints it
    /// in the original (gear, title, subtitle, divider).
    ///
    /// <para>
    /// R74 read four of these off the live build — General, Data, Webhooks and Captcha Providers.
    /// They are per page, not per nav entry: the rail says "Captcha Providers" while the page
    /// itself is titled "3rd Party Captcha Providers".
    /// </para>
    /// </summary>
    public static Control PageHeader(string title, string subtitle) => new StackPanel
    {
        Spacing = 2,
        Margin = new Thickness(0, 0, 0, 10),
        Children =
        {
            new TextBlock { Text = title, FontSize = 20, FontWeight = FontWeight.SemiBold },
            new TextBlock { Text = subtitle, Opacity = 0.6, FontSize = 12 },
        },
    };

    /// <summary>A page: its header over its body.</summary>
    public static Control Page(string title, string subtitle, Control content) => new StackPanel
    {
        Spacing = 6,
        Children = { PageHeader(title, subtitle), content },
    };

    /// <summary>
    /// A bordered card with no title, for a page whose header already carries the name.
    ///
    /// <para>
    /// R75: five Settings pages printed their own name twice — once in the page header and once in
    /// the card right below it ("Custom Stores" over "Custom Stores"). The header is the title; the
    /// card does not need to repeat it.
    /// </para>
    /// </summary>
    public static Border PlainCard(params Control[] children)
    {
        var stack = new StackPanel { Spacing = 8 };
        foreach (var child in children) stack.Children.Add(child);

        return new Border
        {
            BorderThickness = new Thickness(1),
            BorderBrush = new SolidColorBrush(Color.Parse("#2A2E3A")),
            CornerRadius = new CornerRadius(8),
            Padding = new Thickness(12),
            Margin = new Thickness(0, 0, 0, 8),
            Child = stack,
        };
    }

    /// <summary>
    /// A labelled switch: the caption on the left, the green toggle hard right.
    ///
    /// <para>
    /// R78: the live Notifications and Keyboard Shortcuts pages are built out of switches, not
    /// checkboxes — every one of "Enable Notifications", "Allow … Notifications", "In-Bot
    /// Notifications", "Desktop Notifications" and "Sounds" is a toggle on the far right edge.
    /// <see cref="Check"/> draws a checkbox next to its caption, which is a different control in a
    /// different place.
    /// </para>
    /// </summary>
    public static Control Switch(string caption, bool value, Action<bool>? onChanged = null)
    {
        var toggle = new ToggleSwitch
        {
            IsChecked = value,
            OnContent = string.Empty,
            OffContent = string.Empty,
            VerticalAlignment = VerticalAlignment.Center,
            HorizontalAlignment = HorizontalAlignment.Right,
        };

        if (onChanged is not null)
            toggle.IsCheckedChanged += (_, _) => onChanged(toggle.IsChecked == true);

        var row = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        row.Children.Add(new TextBlock
        {
            Text = caption,
            VerticalAlignment = VerticalAlignment.Center,
        });
        Grid.SetColumn(toggle, 1);
        row.Children.Add(toggle);
        return row;
    }

    public static ScrollViewer Scroll(Control content) => new()
    {
        Content = content,
        Margin = new Thickness(0, 8, 0, 0),
        HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled,
    };

    /// <summary>Empty-state placeholder used by list views when nothing is configured yet.</summary>
    public static Control Empty(string message) => new TextBlock
    {
        Text = message,
        Opacity = 0.6,
        FontStyle = FontStyle.Italic,
        Margin = new Thickness(0, 16, 0, 16),
    };

    /// <summary>A simple list bound to a live collection.</summary>
    public static ListBox List(IEnumerable<string> items, double height = 180) => new()
    {
        ItemsSource = new Avalonia.Collections.AvaloniaList<string>(items),
        Height = height,
    };
}
