using Avalonia;
using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Services;
using System.Windows.Input;

namespace Cybersole.Ui.Views.Tasks;

/// <summary>
/// Stagger start (Cybersole.Ui.Views.Tasks.Modals.StaggerStartView) — release tasks in
/// rounds so the store does not see a burst. Recovered keys: TasksToRun, TasksPerRound,
/// Delay, EstimatedTime, StartButton.
/// </summary>
public sealed class StaggerStartView : Window
{

    /// <summary>Closes the dialog without starting anything (bound as <c>Cancel</c>). False when it has no window.</summary>
    private bool CancelCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    private readonly AppServices _services;
    private readonly List<BotTask> _tasks;
    private readonly TextBlock _estimated = UiKit.Status();
    private readonly TextBlock _status = UiKit.Status();

    /// <summary>How many tasks are being staggered (bound as <c>TotalTasks</c>).</summary>
    public int TotalTasks => _tasks.Count;

    /// <summary>
    /// R473: the original binds <c>Start</c> as a **property** on this dialog (binding table + the original's
    /// descriptor table). The behaviour already existed — it was just wired straight to a button; the lambda
    /// closes over the three input boxes, so it stays a lambda and only the exposure changes.
    /// </summary>
    public ICommand Start { get; }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>Cancel</c>; behaviour unchanged (was a method).</summary>
    public ICommand Cancel { get; }

    public StaggerStartView(AppServices services, IEnumerable<BotTask> tasks)
    {
        Cancel = new RelayCommand(() => CancelCore());

        _services = services;
        _tasks = tasks.ToList();

        Title = "Stagger start";
        Width = 480;
        Height = 380;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var toRun = UiKit.Number(_tasks.Count);
        var perRound = UiKit.Number(5);
        var delay = UiKit.Number(2000, 140);
        ToolTip.SetTip(delay, "Delay in milliseconds");

        void Recalculate()
        {
            if (!UiKit.TryReadInt(toRun.Text, out var total)) total = _tasks.Count;
            if (!UiKit.TryReadInt(perRound.Text, out var round) || round <= 0) round = 1;
            if (!UiKit.TryReadInt(delay.Text, out var ms) || ms < 0) ms = 0;

            var rounds = (int)Math.Ceiling(total / (double)round);
            var seconds = Math.Max(0, rounds - 1) * ms / 1000.0;
            _estimated.Text = $"{rounds} round(s), about {TimeSpan.FromSeconds(seconds):mm\\:ss}";
        }

        toRun.TextChanged += (_, _) => Recalculate();
        perRound.TextChanged += (_, _) => Recalculate();
        delay.TextChanged += (_, _) => Recalculate();
        Recalculate();

        Start = new RelayCommand(() =>
        {
            if (!UiKit.TryReadInt(perRound.Text, out var round) || round <= 0) round = 1;
            if (!UiKit.TryReadInt(delay.Text, out var ms) || ms < 0) ms = 0;
            if (!UiKit.TryReadInt(toRun.Text, out var total) || total <= 0) total = _tasks.Count;

            total = Math.Min(total, _tasks.Count);
            _ = RunAsync(_tasks.Take(total), round, TimeSpan.FromMilliseconds(ms));
        });

        var start = UiKit.Button("Start", () => Start.Execute(null));

        Content = new StackPanel
        {
            Spacing = 6,
            Margin = new Thickness(16),
            Children =
            {
                UiKit.Title("Stagger start"),
                UiKit.Caption("Configure how many tasks to start per round."),
                UiKit.Form(
                    UiKit.Row("Tasks to run", toRun),
                    UiKit.Row("Tasks per round", perRound),
                    UiKit.Row("Delay (ms)", delay),
                    UiKit.Row("Estimated time", _estimated)),
                UiKit.Buttons(start, UiKit.Button("Close", Close)),
                _status,
            },
        };
    }

    private async Task RunAsync(IEnumerable<BotTask> tasks, int perRound, TimeSpan delay)
    {
        var all = tasks.ToList();
        var started = 0;

        for (var i = 0; i < all.Count; i += perRound)
        {
            var round = all.Skip(i).Take(perRound).ToList();
            _services.Tasks.StartAll(round);
            started += round.Count;
            _status.Text = $"Started {started}/{all.Count}";

            if (i + perRound < all.Count)
                await Task.Delay(delay).ConfigureAwait(true);
        }

        _status.Text = $"All {all.Count} task(s) started.";
    }
}
