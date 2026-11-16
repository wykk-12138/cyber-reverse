using System.Text;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// Bulk account import (Cybersole.Ui.Views.Accounts.Modals.AccountsCreatorView).
/// Accepts "email:password", "email,password" or "email|password" per line.
///
/// <para>
/// R70: the shipped dialog was driven by hand and reads, top to bottom: the title
/// <c>Add Accounts</c>, the label <c>Accounts</c>, a box watermarked
/// <c>Enter accounts as account:password</c>, a drop zone captioned
/// <c>Or drag and drop a .txt file here</c>, and one button whose caption counts what is about to
/// be imported — <c>Import (3) New Accounts</c>, live as you type. All five strings are locale
/// keys (<c>AccountsCreator.*</c>), so they were never guesses.
/// </para>
///
/// <para>
/// R71: the <c>Group name</c> field is gone. The original has no such field because the group is
/// chosen in the left pane before the dialog opens, and the page now has that pane
/// (<see cref="Views.Accounts.AccountView"/>), so the dialog is told which group it fills instead
/// of asking.
/// </para>
/// </summary>
public sealed class AccountImportWindow : Window
{
    private readonly AccountsDocument _doc;
    private readonly AccountGroup _group;

    private readonly TextBox _lines = new()
    {
        AcceptsReturn = true,
        Height = 260,
        Watermark = "Enter accounts as account:password",
        FontFamily = new FontFamily("Consolas,monospace"),
    };

    private readonly TextBlock _status = new() { Opacity = 0.8 };
    private readonly Button _import;

    public AccountImportWindow(AccountsDocument doc, AccountGroup group)
    {
        _doc = doc;
        _group = group;

        // AccountsCreator.Title
        Title = "Add Accounts";
        Width = 560;
        Height = 480;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        _import = new Button { Padding = new Thickness(16, 5) };
        _import.Click += (_, _) => Import();

        var cancel = new Button { Content = "Cancel" };
        cancel.Click += (_, _) => Close();

        var buttons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Right,
            Children = { cancel, _import },
        };

        // AccountsCreator.DragDrop — printed, so it has to be true: the drop handler is installed
        // below and a dropped .txt file is read into the box rather than silently ignored.
        var dropZone = new Border
        {
            BorderThickness = new Thickness(1),
            BorderBrush = Brushes.Gray,
            CornerRadius = new CornerRadius(6),
            Padding = new Thickness(12, 10),
            Margin = new Thickness(0, 2, 0, 2),
            Child = new TextBlock
            {
                Text = "Or drag and drop a .txt file here",
                Opacity = 0.7,
                HorizontalAlignment = HorizontalAlignment.Center,
            },
        };

        DragDrop.SetAllowDrop(this, true);
        AddHandler(DragDrop.DropEvent, OnDrop);

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                // The group the pane already selected — shown, not editable.
                new TextBlock { Text = group.Display, FontWeight = FontWeight.SemiBold },
                // AccountsCreator.Label
                new TextBlock { Text = "Accounts" },
                _lines,
                dropZone,
                _status,
                buttons,
            },
        };

        // The caption is a count, so it has to follow the box rather than be set once.
        _lines.TextChanged += (_, _) => RefreshCaption();
        RefreshCaption();
    }

    /// <summary><c>AccountsCreator.ImportFormat</c> — <c>Import ({0}) New Accounts</c>.</summary>
    internal static string ImportCaption(int count) => $"Import ({count}) New Accounts";

    private void RefreshCaption() => _import.Content = ImportCaption(ImportParser.ParseAccounts(_lines.Text).Count);

    private void OnDrop(object? sender, DragEventArgs e)
    {
        if (!e.Data.Contains(DataFormats.FileNames)) return;
        var files = e.Data.GetFileNames();
        if (files is null) return;

        var text = new StringBuilder();
        foreach (var path in files)
        {
            if (!path.EndsWith(".txt", StringComparison.OrdinalIgnoreCase)) continue;
            try
            {
                text.AppendLine(System.IO.File.ReadAllText(path));
            }
            catch (Exception)
            {
                // unreadable file: fall through with whatever was read
            }
        }

        if (text.Length > 0) _lines.Text = text.ToString();
    }

    private void Import()
    {
        var parsed = ImportParser.ParseAccounts(_lines.Text);
        if (parsed.Count == 0)
        {
            _status.Text = "Nothing to import (expected email:password per line).";
            return;
        }

        var added = 0;
        var skipped = 0;
        foreach (var (email, password) in parsed)
        {
            // Duplicates are checked across the whole document, not just this group: the same
            // login in two groups is two tasks racing for one account.
            if (_doc.AccountGroups.SelectMany(g => g.Accounts)
                    .Any(a => string.Equals(a.Email, email, StringComparison.OrdinalIgnoreCase)))
            {
                skipped++;
                continue;
            }

            _group.Accounts.Add(new Account { Email = email, Password = password, GroupId = _group.Id });
            added++;
        }

        _servicesSaved?.Invoke();
        _status.Text = $"Imported {added}, skipped {skipped}.";

        // R70: the dialog used to stay open after a successful import, so the only thing that
        // changed on screen was a status line — the table behind it still read "Add some accounts
        // to get started", because the page is rebuilt from the window's Closed handler. Closing
        // is what makes the import visible.
        Close();
    }

    private Action? _servicesSaved;

    /// <summary>Where to persist after a successful import. Called once, after the rows are added.</summary>
    public AccountImportWindow WithSave(Action save)
    {
        _servicesSaved = save;
        return this;
    }
}
