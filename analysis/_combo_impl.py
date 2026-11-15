import io, os
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Controls\ComboBoxEdit.cs"
code = '''using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;

namespace Cybersole.Ui.Views.Controls;

/// <summary>
/// A multi-select dropdown whose choices are shown as removable tokens, with optional group headings
/// (Cybersole.Ui.Controls.ComboBoxEdit, R312).
///
/// <para>
/// The image binds two commands on this control — RemoveTokenCommand and ClearSelectionCommand — and two sibling types in
/// the same namespace: ComboBoxToken (Text) and ComboBoxGroupHeader (Name). That is enough to say what it does and not
/// enough to say what it looks like, so this is the equivalent interaction, not a copy of the original's pixels. No page
/// is wired to it: the binding table names the control, not the screen, and R265's rule is that a control with no proven
/// use does not go on a page to look finished.
/// </para>
/// </summary>
public sealed class ComboBoxEdit : UserControl
{
    /// <summary>One choice. Group is optional; consecutive options with the same group share a heading.</summary>
    public sealed record Option(string Text, string? Group = null);

    /// <summary>A selected value as the control shows it (bound name: ComboBoxToken.Text).</summary>
    public sealed record ComboBoxToken(string Text);

    /// <summary>A heading over a group of options (bound name: ComboBoxGroupHeader.Name).</summary>
    public sealed record ComboBoxGroupHeader(string Name);

    private readonly List<string> _selected = new();
    private readonly StackPanel _tokens = new() { Orientation = Orientation.Horizontal, Spacing = 4 };
    private readonly ComboBox _combo = new() { Width = 240 };
    private readonly List<Option> _options = new();

    /// <summary>The choices, in the order they were added.</summary>
    public IReadOnlyList<Option> Options => _options;

    /// <summary>The selected texts, in selection order.</summary>
    public IReadOnlyList<string> Selected => _selected;

    /// <summary>The dropdown rows, including group headings.</summary>
    public IReadOnlyList<object> Rows => (_combo.ItemsSource as IEnumerable<object>)?.ToList() ?? new List<object>();

    /// <summary>Raised after any change to Selected.</summary>
    public event EventHandler? Changed;

    public ComboBoxEdit()
    {
        _combo.SelectionChanged += (_, _) =>
        {
            if (_combo.SelectedItem is Option option) Add(option.Text);
        };

        Content = new StackPanel
        {
            Spacing = 4,
            Children = { _tokens, _combo },
        };
    }

    /// <summary>Replaces the choices and rebuilds the dropdown, inserting a heading wherever the group changes.</summary>
    public void SetOptions(IEnumerable<Option> options)
    {
        _options.Clear();
        _options.AddRange(options);

        var rows = new List<object>();
        string? group = null;
        foreach (var option in _options)
        {
            if (option.Group is not null && option.Group != group)
            {
                rows.Add(new ComboBoxGroupHeader(option.Group));
                group = option.Group;
            }
            rows.Add(option);
        }

        _combo.ItemsSource = rows;
        _combo.SelectedIndex = -1;
    }

    /// <summary>Selects a text; ignored when it is not one of the options or already selected.</summary>
    public bool Add(string text)
    {
        if (_options.Count > 0 && !_options.Any(o => o.Text == text)) return false;
        if (_selected.Contains(text)) return false;

        _selected.Add(text);
        RebuildTokens();
        Changed?.Invoke(this, EventArgs.Empty);
        return true;
    }

    /// <summary>Removes the first token with this text (bound as RemoveTokenCommand). False when absent.</summary>
    public bool RemoveToken(string text)
    {
        var index = _selected.IndexOf(text);
        if (index < 0) return false;

        _selected.RemoveAt(index);
        RebuildTokens();
        Changed?.Invoke(this, EventArgs.Empty);
        return true;
    }

    /// <summary>Drops every token (bound as ClearSelectionCommand). Returns how many were removed.</summary>
    public int ClearSelection()
    {
        var count = _selected.Count;
        if (count == 0) return 0;

        _selected.Clear();
        RebuildTokens();
        Changed?.Invoke(this, EventArgs.Empty);
        return count;
    }

    private void RebuildTokens()
    {
        _tokens.Children.Clear();
        foreach (var text in _selected)
        {
            var label = new TextBlock { Text = text, VerticalAlignment = VerticalAlignment.Center };
            var remove = new Button { Content = "\\u00d7", Padding = new Thickness(4, 0) };
            var captured = text;
            remove.Click += (_, _) => RemoveToken(captured);

            _tokens.Children.Add(new StackPanel
            {
                Orientation = Orientation.Horizontal,
                Spacing = 2,
                Children = { label, remove },
            });
        }
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('written', os.path.getsize(p), 'bytes')
