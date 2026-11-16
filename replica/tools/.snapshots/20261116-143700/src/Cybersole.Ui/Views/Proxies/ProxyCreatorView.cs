using System;
using System.Linq;
using Avalonia;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;

namespace Cybersole.Ui.Views.Proxies;

/// <summary>
/// Creates proxies — the modal the original calls <c>Proxies.Modals.ProxyCreatorView</c> (R204).
///
/// <para>
/// Two paths, because the original has two: type one proxy in, or <b>drop</b> a list onto it. The drop half is named by
/// the image itself (<c>0x06e5071c  ProxyCreator.DragDrop</c>), which is why this view handles
/// <see cref="DragDrop.DropEvent"/> for both text and files rather than only offering a text box.
/// </para>
///
/// <para>
/// The page used to have one way in — a bulk "Add Proxies" importer — so "create exactly one, carefully" had no path,
/// and a dropped file had nowhere to land.
/// </para>
/// </summary>
public sealed class ProxyCreatorView : UserControl
{

    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>
    public bool CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    private readonly ProxyCreatorModel _model = new ProxyCreatorModel();
    private readonly TextBox _text;
    private readonly TextBox _host;
    private readonly TextBox _port;
    private readonly TextBox _user;
    private readonly TextBox _password;
    private readonly ComboBox _scheme;
    private readonly TextBlock _status;

    /// <summary>Raised once per accepted batch, so the caller owns adding to a group and saving.</summary>
    public event Action<IReadOnlyList<Proxy>>? Created;

    /// <summary>Bound as <c>Close</c>; closes the hosting window (was a bool method).</summary>
    public ICommand Close { get; }

    public ProxyCreatorView()
    {
        Close = new RelayCommand(() => CloseCore());

        _text = UiKit.Text(string.Empty, watermark: "host:port:user:pass, one per line", width: double.NaN);
        _text.AcceptsReturn = true;
        _text.Height = 110;
        _text.TextWrapping = TextWrapping.Wrap;
        _host = UiKit.Text(string.Empty, watermark: "host", width: 190);
        _port = UiKit.Text(string.Empty, watermark: "port", width: 80);
        _user = UiKit.Text(string.Empty, watermark: "username", width: 150);
        _password = UiKit.Text(string.Empty, watermark: "password", width: 150);
        _scheme = new ComboBox
        {
            Width = 110,
            ItemsSource = new[] { "http", "https", "socks4", "socks5" },
            SelectedIndex = 0,
        };
        _status = new TextBlock { Opacity = 0.7, FontSize = 11 };

        Content = Build();
        DragDrop.SetAllowDrop(this, true);
        AddHandler(DragDrop.DragOverEvent, OnDragOver);
        AddHandler(DragDrop.DropEvent, OnDrop);
    }

    private Control Build()
    {
        var panel = new StackPanel { Spacing = 10, Margin = new Thickness(16) };

        panel.Children.Add(new TextBlock { Text = "Add Proxy", FontSize = 15, FontWeight = FontWeight.SemiBold });

        panel.Children.Add(_text);
        panel.Children.Add(new TextBlock
        {
            Text = "…or drop a list here (a .txt file works too)",
            Opacity = 0.6,
            FontSize = 11,
        });

        var bulk = new Button { Content = "Add from text" };
        bulk.Click += (_, _) => Commit(_model.AddFromText(_text.Text));
        panel.Children.Add(bulk);

        panel.Children.Add(new Border
        {
            Height = 1, Background = Brushes.Gray, Opacity = 0.2, Margin = new Thickness(0, 4),
        });

        var one = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        foreach (var control in new Control[] { _host, _port, _user, _password, _scheme })
            one.Children.Add(control);
        panel.Children.Add(one);

        var single = new Button { Content = "Add one" };
        single.Click += (_, _) => CommitSingle();
        panel.Children.Add(single);

        panel.Children.Add(_status);
        return panel;
    }

    private void CommitSingle()
    {
        var proxy = _model.AddOne(_host.Text, _port.Text, _user.Text, _password.Text,
            (_scheme.SelectedItem as string) ?? "http");

        if (proxy is null)
        {
            // keep the fields as typed: clearing them would make the user retype after a typo in one of them
            _status.Text = "host and a port between 1 and 65535 are required";
            return;
        }

        _status.Text = "added " + proxy.Address;
        Created?.Invoke(new[] { proxy });
    }

    private void Commit(ProxyCreatorModel.Result result)
    {
        if (result.Total == 0) { _status.Text = "nothing to add"; return; }

        _status.Text = result.Accepted.Count + " added"
            + (result.Rejected > 0 ? ", " + result.Rejected + " line(s) not understood" : string.Empty);

        if (result.Accepted.Count > 0) Created?.Invoke(result.Accepted);
    }

    private void OnDragOver(object? sender, DragEventArgs e)
    {
        e.DragEffects = e.Data.Contains(DataFormats.Text) || e.Data.Contains(DataFormats.Files)
            ? DragDropEffects.Copy
            : DragDropEffects.None;
        e.Handled = true;
    }

    private void OnDrop(object? sender, DragEventArgs e)
    {
        e.Handled = true;

        if (e.Data.Contains(DataFormats.Text))
        {
            Commit(_model.AddFromText(e.Data.GetText()));
            return;
        }

        if (!e.Data.Contains(DataFormats.Files)) return;

        var paths = e.Data.GetFiles()?.Select(f => f.Path.LocalPath).Where(p => p is not null).ToArray();
        if (paths is null || paths.Length == 0) return;

        var text = string.Join('\n', paths.Select(ProxyCreatorModel.ReadDroppedFile).Where(t => t is not null));
        Commit(_model.AddFromText(text));
    }
}
