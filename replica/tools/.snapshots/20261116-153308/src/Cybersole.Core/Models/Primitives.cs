using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace Cybersole.Core.Models;

/// <summary>Minimal INotifyPropertyChanged base used across models and view models.</summary>
public abstract class ObservableObject : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    protected void OnPropertyChanged([CallerMemberName] string? name = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));

    protected bool SetProperty<T>(ref T field, T value, [CallerMemberName] string? name = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value)) return false;
        field = value;
        OnPropertyChanged(name);
        return true;
    }
}

/// <summary>Async command with an <see cref="IsExecuting"/> gate (Cybersole.Models.AsyncCommand).</summary>
public sealed class AsyncCommand : ICommand
{
    private readonly Func<Task> _execute;
    private readonly Func<bool>? _canExecute;
    private bool _isExecuting;

    public AsyncCommand(Func<Task> execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool IsExecuting
    {
        get => _isExecuting;
        private set
        {
            if (_isExecuting == value) return;
            _isExecuting = value;
            RaiseCanExecuteChanged();
        }
    }

    public bool CanExecute(object? parameter)
        => !_isExecuting && (_canExecute?.Invoke() ?? true);

    public async void Execute(object? parameter)
    {
        if (!CanExecute(parameter)) return;
        IsExecuting = true;
        try
        {
            await _execute().ConfigureAwait(true);
        }
        finally
        {
            IsExecuting = false;
        }
    }

    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}

/// <summary>Simple sync command.</summary>
public sealed class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;

    public void Execute(object? parameter) => _execute();

    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}

/// <summary>Editable scalar used by grid editors; <see cref="HasMultiple"/> marks mixed values.</summary>
public sealed class EditValue<T> : ObservableObject
{
    private T? _value;
    private bool _hasMultiple;

    public T? Value
    {
        get => _value;
        set => SetProperty(ref _value, value);
    }

    public bool HasMultiple
    {
        get => _hasMultiple;
        set => SetProperty(ref _hasMultiple, value);
    }

    public EditValue() { }
    public EditValue(T value) => _value = value;
}

/// <summary>Status pill shown in grids (Cybersole.Models.Status).</summary>
public sealed class Status : ObservableObject
{
    private string _color = "#6E7681";
    private string _icon = "circle";
    private string _text = "Idle";

    public string Color { get => _color; set => SetProperty(ref _color, value); }
    public string Icon { get => _icon; set => SetProperty(ref _icon, value); }
    public string Text { get => _text; set => SetProperty(ref _text, value); }

    /// <summary>
    /// Whether the status chip is clickable — the original binds this on <c>Models.Status</c>
    /// (analysis/xaml_bindings.json). A chip with a click handler says so here rather than by cursor shape.
    /// </summary>
    public bool Clickable { get; set; }

    public static Status Idle => new() { Color = "#6E7681", Icon = "circle", Text = "Idle" };
    public static Status Running => new() { Color = "#3FB950", Icon = "play", Text = "Running" };
    public static Status Failed => new() { Color = "#F85149", Icon = "x", Text = "Failed" };
    public static Status Success => new() { Color = "#2EA043", Icon = "check", Text = "Success" };

    /// <summary>
    /// The label, not the type name.
    /// </summary>
    /// <remarks>
    /// R66: a proxy table rendered <c>proxy.Status.ToString()</c> and showed
    /// "Cybersole.Core.Models.Status" in the Status column. This is a plain class, so the default
    /// ToString was the only thing available. Overriding it means the next caller who writes
    /// <c>.ToString()</c> — or interpolates the object into a string — gets the label instead of
    /// the namespace.
    /// </remarks>
    public override string ToString() => Text;
}

/// <summary>Time-span option for dropdowns (Cybersole.Ui.Views.TimeSpanOption).</summary>
public sealed class TimeSpanOption
{
    public string Name { get; set; } = string.Empty;
    public TimeSpan Value { get; set; }
}
