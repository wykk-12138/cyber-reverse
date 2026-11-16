using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;

namespace Cybersole.Ui.Views;

/// <summary>
/// 3DS / OTP prompt raised by the checkout pipeline (settings.autoOpen3DS drives auto-open).
/// The window is modal and resolves a <see cref="TaskCompletionSource{TResult}"/>.
/// </summary>
public sealed class ThreeDSWindow : Window
{
    private readonly TextBox _code = new() { Watermark = "one-time code", Width = 260 };
    private readonly TextBlock _hint = new() { Opacity = 0.75, TextWrapping = TextWrapping.Wrap };
    private readonly TaskCompletionSource<string?> _tcs = new();

    public ThreeDSWindow(string store, string profile)
    {
        Title = $"3DS — {store}";
        Width = 420;
        Height = 240;
        CanResize = false;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        _hint.Text = $"Enter the one-time code for {profile} ({store}).";

        var submit = new Button { Content = "Submit", Padding = new Thickness(16, 5), IsDefault = true };
        submit.Click += (_, _) => CloseWithResult(_code.Text);

        var cancel = new Button { Content = "Cancel" };
        cancel.Click += (_, _) => CloseWithResult(null);

        var root = new StackPanel
        {
            Spacing = 12,
            Margin = new Thickness(18),
            Children =
            {
                _hint,
                _code,
                new StackPanel
                {
                    Orientation = Orientation.Horizontal,
                    Spacing = 8,
                    HorizontalAlignment = HorizontalAlignment.Right,
                    Children = { cancel, submit },
                },
            },
        };

        Content = root;
    }

    /// <summary>Await the user's code (null when cancelled).</summary>
    public Task<string?> Result => _tcs.Task;

    protected override void OnClosed(EventArgs e)
    {
        if (!_tcs.Task.IsCompleted) _tcs.TrySetResult(null);
        base.OnClosed(e);
    }

    private void CloseWithResult(string? code)
    {
        if (!_tcs.Task.IsCompleted) _tcs.TrySetResult(code);

        // ShowDialog<T> resolves to whatever Close(object?) was handed. Calling the parameterless
        // base.Close() left it at default(T) — null for string? — so the caller never saw the code
        // and the status line never updated. Round 121.
        Close(code);
    }
}
