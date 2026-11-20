using System.Globalization;
using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views.SmartActions;

/// <summary>
/// Smart actions list (Cybersole.Ui.Views.SmartActions.SmartActionsView) — NewAction / search
/// / clone / delete / edit / publish / view logs, plus the per-row trigger and last-run text.
/// </summary>
public sealed class SmartActionsView : UserControl
{

    // ------------------------------------------------ copy from the image's locale (R413)
    //
    // The SmartActions.* strings that had no counterpart, verbatim (same table shape as the other pages).
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["ActionsMoreFormat"] = "{0} ({1} more)",   // SmartActions.Actions.MoreFormat
        ["ChangeTriggerMessage"] = "Changing the trigger will reset all filters and actions. Are you sure?",   // SmartActions.ChangeTrigger.Message
        ["ChangeTriggerTitle"] = "Change Trigger?",   // SmartActions.ChangeTrigger.Title
        ["PublishFormat"] = "Publish {0}",   // SmartActions.Context.PublishFormat
        ["EmptyNoActionsSubtitle"] = "Add some smart actions to get started",   // SmartActions.Empty.NoActions.Subtitle
        ["EmptyNoResultsSubtitle"] = "There are no results matching your search",   // SmartActions.Empty.NoResults.Subtitle
        ["FiltersCountFormat"] = "{0} Filters",   // SmartActions.Filters.CountFormat
        ["FiltersNone"] = "No Filters",   // SmartActions.Filters.None
        ["FiltersOne"] = "1 Filter",   // SmartActions.Filters.One
        ["HeaderFormat"] = "Smart Actions ({0})",   // SmartActions.HeaderFormat
        ["LastRunFormat"] = "Triggered {0} ({1})",   // SmartActions.LastRun.Format
        ["NewAction"] = "New Action",   // SmartActions.NewAction
        ["SearchPlaceholder"] = "Search Smart Actions",   // SmartActions.SearchPlaceholder
    };

    /// <summary>One of the image's smart-action strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;

    /// <summary>The filters caption with the image's zero / one / many forms (SmartActions.Filters.*).</summary>
    public static string FiltersCaption(int count) => count switch
    {
        0 => Text("FiltersNone"),
        1 => Text("FiltersOne"),
        _ => string.Format(Text("FiltersCountFormat"), count),
    };
    private readonly AppServices _services;
    private readonly ListBox _rows = new() { Height = 320 };
    private readonly TextBox _search = new() { Watermark = "Search actions", Width = 240 };
    private readonly TextBlock _status = UiKit.Status();

    /// <summary>
    /// Shows the run history (bound as <c>ViewLogs</c>). The history window was already written; nothing opened it from
    /// this page.
    /// </summary>
    /// <summary>Opens the creator for a brand-new action (bound as <c>OpenCreator</c>).</summary>
    private void OpenCreatorCore() => OpenActionEditor(null);

    /// <summary>
    /// The live time this page shows (bound as <c>Clock</c>, getter only).
    ///
    /// <para>
    /// Evidence: <c>docs/xaml_bindings.json</c> records <c>SmartActionsView.Clock!Getter</c> with no
    /// setter, and the same member on <c>MainWindow</c> and <c>ModalView.NotificationView</c>
    /// (descriptors at <c>analysis/pe_strings.txt</c> 0x0320f03f / 0x0321009f / 0x0321dab0). The
    /// replica's <c>MainWindow.Clock</c> already formats the nav-bar clock; this is the same value on
    /// the page whose binding table names it. Reading it is all the evidence supports — no timer is
    /// invented here, because the getter form says the page re-reads it, not that the page owns it.
    /// </para>
    /// </summary>
    public string Clock
    {
        get
        {
            var format = _services.Config.Settings.ClockFormat;
            if (string.IsNullOrWhiteSpace(format)) format = "HH:mm:ss";
            try
            {
                return DateTime.Now.ToString(format, CultureInfo.InvariantCulture);
            }
            catch (FormatException)
            {
                // A hand-typed format that Windows rejects must not blank the page.
                return DateTime.Now.ToString("HH:mm:ss", CultureInfo.InvariantCulture);
            }
        }
    }

    private void ViewLogsCore()
    {
        if (TopLevel.GetTopLevel(this) is Window owner) new HistoryWindow(_services).Show(owner);
    }

    /// <summary>
    /// R475: the original binds <c>Edit</c> / <c>Clone</c> / <c>Delete</c> as **properties** on this view.
    /// All three already worked — they were lambdas wired straight to buttons — so this only moves them where
    /// the binding expects them. <c>Export</c> is deliberately absent: nothing in the replica says what it
    /// exports, and an invented format would be a fake match (same call as `ProxyView.TestAll`).
    /// </summary>
    public ICommand Edit { get; }

    /// <inheritdoc cref="Edit"/>
    public ICommand Clone { get; }

    /// <inheritdoc cref="Edit"/>
    public ICommand Delete { get; }

    // R500: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>OpenCreator</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenCreator { get; }

    /// <summary>Bound as <c>ViewLogs</c>; behaviour unchanged (was a method).</summary>
    public ICommand ViewLogs { get; }

    public SmartActionsView(AppServices services)
    {
        OpenCreator = new RelayCommand(OpenCreatorCore);
        ViewLogs = new RelayCommand(ViewLogsCore);

        _services = services;
        Edit = new RelayCommand(() => OpenActionEditor(null));
        Clone = new RelayCommand(CloneSelected);
        Delete = new RelayCommand(DeleteSelected);

        _search.TextChanged += (_, _) => Refresh();

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                new StackPanel
                {
                    Orientation = Orientation.Horizontal,
                    Spacing = 8,
                    Children =
                    {
                        UiKit.Title("Smart actions"),
                        _search,
                    },
                },
                _rows,
                UiKit.Buttons(
                    UiKit.Button("New action", () =>
                    {
                        var action = new SmartAction
                        {
                            Name = $"Action {_services.Config.SmartActions.Actions.Count + 1}",
                            Trigger = SmartTrigger.CheckoutSuccess,
                            Kind = SmartActionKind.Webhook,
                            Enabled = true,
                        };
                        _services.Config.SmartActions.Actions.Add(action);
                        _services.Config.Save();
                        Refresh();
                        _status.Text = "Action created.";
                    }),
                    UiKit.Button("Edit", () => Edit.Execute(null)),
                    UiKit.Button("Clone", () => Clone.Execute(null)),
                    UiKit.Button("Delete", () => Delete.Execute(null)),
                    UiKit.Button("Publish", () =>
                    {
                        // R256: this used to say templates were not implemented. The locale has a whole
                        // PublishTemplate dialog, the dialog was already written 480 lines up this same file,
                        // and the only genuinely missing piece was somewhere to write. See
                        // PublishTemplateModal and SmartActionsDocument.Templates.
                        var target = Selected();
                        if (target is null) { Status("Select an action to publish."); return; }

                        if (TopLevel.GetTopLevel(this) is not Window owner)
                        { Status("No owner window - cannot open the publish dialog."); return; }

                        var modal = new PublishTemplateModal(_services, target);
                        modal.Closed += (_, _) => Status(modal.Published
                            ? $"Published \"{target.Name}\" as a template."
                            : "Publish cancelled.");
                        _ = modal.ShowDialog(owner);
                    }),
                    UiKit.Button("View logs", () =>
                    {
                        var target = Selected();
                        Status(target is null ? "Select an action." : $"{target.Name}: {target.LastResult ?? "never run"}");
                    })),
                _status,
            },
        };

        Refresh();
    }

    private void Status(string text) => _status.Text = text;

    /// <summary>
    /// Open the smart-action editor.
    ///
    /// "Edit" used to only write "Edit the selected action." to the status line while
    /// SmartActionEditorWindow sat unused. Same defect as TasksViews (rounds 97/99) and the
    /// Profiles page (round 100).
    /// </summary>
    private void OpenActionEditor(object? existing)
    {
        var owner = TopLevel.GetTopLevel(this) as Window;
        if (owner is null)
        {
            Status("No owner window — cannot open the editor.");
            return;
        }

        var editor = new SmartActionEditorWindow(_services);
        editor.Closed += (_, _) => { _services.Config.Save(); Refresh(); };
        _ = editor.ShowDialog(owner);
        Status(existing is null ? "Smart-action editor opened." : $"Editing {existing}.");
    }

    /// <summary>Duplicates the selected action, filters included (lifted out of the old button lambda, R475).</summary>
    private void CloneSelected()
    {
        var src = Selected();
        if (src is null) return;
        _services.Config.SmartActions.Actions.Add(new SmartAction
        {
            Name = src.Name + " copy",
            Trigger = src.Trigger,
            Kind = src.Kind,
            Target = src.Target,
            StoreFilter = src.StoreFilter,
            MinPrice = src.MinPrice,
            Enabled = src.Enabled,
            Filters = src.Filters.Select(f => new SmartActionFilter
            {
                Field = f.Field,
                Operator = f.Operator,
                Value = f.Value,
            }).ToList(),
        });
        _services.Config.Save();
        Refresh();
        _status.Text = "Action cloned.";
    }

    /// <summary>Removes the selected action (lifted out of the old button lambda, R475).</summary>
    private void DeleteSelected()
    {
        var target = Selected();
        if (target is null) return;
        _services.Config.SmartActions.Actions.Remove(target);
        _services.Config.Save();
        Refresh();
        _status.Text = "Action deleted.";
    }

    private SmartAction? Selected()
    {
        var index = _rows.SelectedIndex;
        var visible = Visible();
        if (index < 0 || index >= visible.Count) return null;
        return visible[index];
    }

    private List<SmartAction> Visible()
    {
        var filter = _search.Text?.Trim() ?? string.Empty;
        return _services.Config.SmartActions.Actions
            .Where(a => filter.Length == 0 ||
                        a.Name.Contains(filter, StringComparison.OrdinalIgnoreCase) ||
                        a.Trigger.ToString().Contains(filter, StringComparison.OrdinalIgnoreCase))
            .ToList();
    }

    public void Refresh()
    {
        var visible = Visible();
        _rows.ItemsSource = visible.Count == 0
            ? new List<string> { _search.Text is { Length: > 0 } ? "(no results)" : "(no actions yet)" }
            : visible.Select(a =>
                $"{(a.Enabled ? "*" : "-")} {a.Name}  ·  {a.Trigger}  →  {a.Kind}" +
                $"  ·  filters={a.Filters.Count}" +
                $"  ·  last={(a.LastRun is { } t ? t.ToString("HH:mm:ss") : "never")}").ToList();
    }
}

/// <summary>
/// Three-step creator (Cybersole.Ui.Views.SmartActions.SmartActionsCreator) — Step1Trigger /
/// Step2Filters / Step3Actions with Back / Complete.
/// </summary>
public sealed class SmartActionsCreator : UserControl
{
    /// <summary>Bound as <c>Clone</c>; runs <c>CloneCore()</c>.</summary>
    public ICommand Clone { get; }

    private readonly AppServices _services;
    private readonly SmartAction _action;
    private readonly StackPanel _body = new() { Spacing = 6 };
    private readonly TextBlock _step = UiKit.Status();
    private readonly TextBlock _status = UiKit.Status();
    private readonly List<SmartActionFilter> _filters = new();
    private int _index;

    /// <summary>
    /// R484: the original binds <c>Save</c> as a **property** on this editor. `Save()` had no call sites outside
    /// the class, so it is renamed `SaveCore` to free the bound name; behaviour unchanged.
    /// </summary>
    public ICommand Save { get; }

    // R497: bound names for actions that already existed as no-arg methods.
    /// <summary>Bound as <c>Minimise</c>; behaviour unchanged (was a method).</summary>
    public ICommand Minimise { get; }

    /// <summary>Bound as <c>Exit</c>; behaviour unchanged (was a method).</summary>
    public ICommand Exit { get; }

    /// <summary>Bound as <c>CloseOverlay</c>; behaviour unchanged (was a method).</summary>
    public ICommand CloseOverlay { get; }

    public SmartActionsCreator(AppServices services, SmartAction? existing = null)
    {
        Clone = new RelayCommand(() => CloneCore());
        Minimise = new RelayCommand(MinimiseCore);
        Exit = new RelayCommand(ExitCore);
        CloseOverlay = new RelayCommand(CloseOverlayCore);

        Save = new RelayCommand(SaveCore);
        _services = services;
        _action = existing ?? new SmartAction
        {
            Name = "New action",
            Trigger = SmartTrigger.CheckoutSuccess,
            Kind = SmartActionKind.Webhook,
        };
        _filters.AddRange(_action.Filters);
        IsEditing = existing is not null;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title(existing is null ? "New smart action" : $"Edit {existing.Name}"),
                _step,
                _body,
                UiKit.Buttons(
                    UiKit.Button("Back", () => Navigate(_index - 1)),
                    UiKit.Button("Complete", () => Navigate(_index + 1)),
                    UiKit.Button("Save", () => Save.Execute(null))),
                _status,
            },
        };

        Navigate(0);
    }

    public int Step => _index;

    // ------------------------------------------------ bound commands (R230)
    //
    // The original binds nineteen members on SmartActionsCreator (analysis/xaml_bindings.json):
    //   AddAction, AddFilter, AddInput, Clone, CloseOverlay, Delete, DeleteAction, DeleteFilter, DeleteInput, DeleteParam,
    //   Exit, IsEditing, Minimise, Save, Settings, SmartAction, TimeSpans, ToggleFilterBehaviour, UseTemplate
    // The ones below have a model to stand on. The rest are listed in docs/XAML_BINDINGS.md as blocked, with the reason.

    /// <summary>True when the creator was opened on an existing action (bound as <c>IsEditing</c>).</summary>
    public bool IsEditing { get; private set; }

    /// <summary>The action being edited (bound as <c>SmartAction</c>).</summary>
    public SmartAction SmartAction => _action;

    /// <summary>Adds an action step to the rule (bound as <c>AddAction</c>).</summary>
    public SmartActionStep AddAction(SmartActionKind kind = SmartActionKind.Notification, string? name = null)
    {
        var step = new SmartActionStep
        {
            Name = string.IsNullOrWhiteSpace(name) ? "Action " + (_action.Actions.Count + 1) : name!.Trim(),
            Kind = kind,
            Target = _action.Target,
        };
        _action.Actions.Add(step);
        if (_index != 2) Navigate(2); else Navigate(2);
        return step;
    }

    /// <summary>Removes the action at <paramref name="index"/> (bound as <c>DeleteAction</c>).</summary>
    public bool DeleteAction(int index)
    {
        if (index < 0 || index >= _action.Actions.Count) return false;
        _action.Actions.RemoveAt(index);
        if (_index == 2) Navigate(2);
        return true;
    }

    /// <summary>Adds an input to the filter at <paramref name="filterIndex"/> (bound as <c>AddInput</c>).</summary>
    public SmartActionFilterInput? AddInput(int filterIndex, string filterName, string input)
    {
        if (filterIndex < 0 || filterIndex >= _filters.Count) return null;

        var entry = new SmartActionFilterInput { Filter = filterName, Input = input };
        _filters[filterIndex].Inputs.Add(entry);
        if (_index == 1) Navigate(1);
        return entry;
    }

    /// <summary>Removes an input from a filter (bound as <c>DeleteInput</c>).</summary>
    public bool DeleteInput(int filterIndex, int inputIndex)
    {
        if (filterIndex < 0 || filterIndex >= _filters.Count) return false;
        var inputs = _filters[filterIndex].Inputs;
        if (inputIndex < 0 || inputIndex >= inputs.Count) return false;
        inputs.RemoveAt(inputIndex);
        if (_index == 1) Navigate(1);
        return true;
    }

    /// <summary>
    /// The filters as rows the editor can render (R317). IsFirst is decided by position — the member's plainest reading —
    /// and Passed is left false here: judging needs a CheckoutEvent, which belongs to the engine (see FilterRow).
    /// </summary>
    public IReadOnlyList<FilterRow> FilterRows =>
        _filters.Select((f, index) => new FilterRow(f, passed: false, isFirst: index == 0)).ToList();

    /// <summary>The steps as rows the editor can render; Result and Tooltip stay empty until a step has run.</summary>
    public IReadOnlyList<ActionRow> ActionRows =>
        _action.Actions.Select((a, index) => new ActionRow(a, index == 0)).ToList();

    /// <summary>The templates a new action can be built from (bound as <c>UseTemplate</c> targets).</summary>
    public IReadOnlyList<PublishedTemplate> Templates => _services.Config.SmartActions.Templates;

    /// <summary>
    /// Builds this action from a published template (bound as <c>UseTemplate</c>).
    ///
    /// <para>
    /// A template carries only metadata — a title, a description, a group and the id of the action it was published from
    /// (<see cref="PublishedTemplate.SourceActionId"/>) — so using one means copying that source action's filters and
    /// steps. The name of the action being edited is left alone: a template is a starting point.
    /// </para>
    /// </summary>
    public bool UseTemplate(string title)
    {
        var template = Templates.FirstOrDefault(t => t.Title == title);
        if (template is null || string.IsNullOrEmpty(template.SourceActionId)) return false;

        var source = _services.Config.SmartActions.Actions.FirstOrDefault(a => a.Id == template.SourceActionId);
        if (source is null) return false;

        _filters.Clear();
        foreach (var filter in source.Filters)
            _filters.Add(new SmartActionFilter
            {
                Field = filter.Field,
                Operator = filter.Operator,
                Value = filter.Value,
                Behaviour = filter.Behaviour,
                Inputs = filter.Inputs.Select(i => new SmartActionFilterInput { Filter = i.Filter, Input = i.Input }).ToList(),
            });

        _action.Actions = source.Actions.Select(a => new SmartActionStep
        {
            Name = a.Name,
            Kind = a.Kind,
            Target = a.Target,
            Config = a.Config.Select(cfg => new SmartActionStepConfig { Name = cfg.Name, Required = cfg.Required }).ToList(),
        }).ToList();

        if (_index == 1) Navigate(1);
        if (_index == 2) Navigate(2);
        return true;
    }

    /// <summary>
    /// Removes a parameter from an action step (bound as <c>DeleteParam</c>). The parameters are
    /// <see cref="SmartActionStepConfig"/> entries — the same "Name / Required" pair the original binds as ActionConfig.
    /// </summary>
    public bool DeleteParam(int stepIndex, int paramIndex)
    {
        if (stepIndex < 0 || stepIndex >= _action.Actions.Count) return false;

        var config = _action.Actions[stepIndex].Config;
        if (paramIndex < 0 || paramIndex >= config.Count) return false;

        config.RemoveAt(paramIndex);
        if (_index == 2) Navigate(2);
        return true;
    }

    /// <summary>Adds a parameter to an action step.</summary>
    public SmartActionStepConfig? AddParam(int stepIndex, string name, bool required = false)
    {
        if (stepIndex < 0 || stepIndex >= _action.Actions.Count) return null;

        var entry = new SmartActionStepConfig { Name = name, Required = required };
        _action.Actions[stepIndex].Config.Add(entry);
        if (_index == 2) Navigate(2);
        return entry;
    }

    /// <summary>Flips a filter between "And" and "Or" (bound as <c>ToggleFilterBehaviour</c>).</summary>
    public string? ToggleFilterBehaviour(int filterIndex)
    {
        if (filterIndex < 0 || filterIndex >= _filters.Count) return null;

        var filter = _filters[filterIndex];
        filter.Behaviour = string.Equals(filter.Behaviour, "Or", StringComparison.OrdinalIgnoreCase) ? "And" : "Or";
        if (_index == 1) Navigate(1);
        return filter.Behaviour;
    }

    /// <summary>Adds a filter and repaints step 2 (bound as <c>AddFilter</c>).</summary>
    public void AddFilter(SmartActionFilter filter)
    {
        _filters.Add(filter);
        _action.Filters.Add(filter);
        if (_index != 1) Navigate(1);
        else Navigate(1);
    }

    /// <summary>Removes the filter at <paramref name="index"/> (bound as <c>DeleteFilter</c>).</summary>
    public bool DeleteFilter(int index)
    {
        if (index < 0 || index >= _filters.Count) return false;
        var filter = _filters[index];
        _filters.RemoveAt(index);
        _action.Filters.Remove(filter);
        if (_index == 1) Navigate(1);
        return true;
    }

    /// <summary>Duplicates the action and opens the copy (bound as <c>Clone</c>).</summary>
    public SmartAction CloneCore()
    {
        var copy = new SmartAction
        {
            Name = _action.Name + " copy",
            Trigger = _action.Trigger,
            Kind = _action.Kind,
            Target = _action.Target,
            RunOnce = _action.RunOnce,
            RunInterval = _action.RunInterval,
            Notifications = _action.Notifications,
            Enabled = _action.Enabled,
        };
        foreach (var filter in _filters) copy.Filters.Add(new SmartActionFilter
        {
            Field = filter.Field, Operator = filter.Operator, Value = filter.Value,
        });

        _services.Config.SmartActions.Actions.Add(copy);
        _services.Config.Save();
        _status.Text = "Cloned to " + copy.Name;
        return copy;
    }

    /// <summary>Minimises the hosting window (bound as <c>Minimise</c>).</summary>
    private void MinimiseCore()
    {
        if (TopLevel.GetTopLevel(this) is Window w) w.WindowState = WindowState.Minimized;
    }

    /// <summary>Closes the hosting window (bound as <c>Exit</c>).</summary>
    private void ExitCore()
    {
        if (TopLevel.GetTopLevel(this) is Window w) w.Close();
    }

    /// <summary>Dismisses the overlay the creator is hosted in, if any (bound as <c>CloseOverlay</c>).</summary>
    private void CloseOverlayCore() => ExitCore();

    private void Navigate(int index)
    {
        _index = Math.Clamp(index, 0, 2);
        _body.Children.Clear();

        switch (_index)
        {
            case 0:
                _step.Text = "Step 1 of 3 — trigger";
                BuildTrigger();
                break;
            case 1:
                _step.Text = "Step 2 of 3 — filters";
                BuildFilters();
                break;
            default:
                _step.Text = "Step 3 of 3 — actions";
                BuildActions();
                break;
        }

        if (_index == 2) _status.Text = "Review and save.";
        else if (_index == 0) _status.Text = "Choose what fires this action.";
        else _status.Text = "All filters must pass; an empty chain always passes.";
    }

    private void BuildTrigger()
    {
        var name = UiKit.Text(_action.Name, watermark: "Action name");
        name.TextChanged += (_, _) => _action.Name = name.Text ?? _action.Name;

        var trigger = UiKit.Combo(Enum.GetNames<SmartTrigger>(), (int)_action.Trigger);
        trigger.SelectionChanged += (_, _) =>
            _action.Trigger = (SmartTrigger)Math.Max(0, trigger.SelectedIndex);

        var store = UiKit.Text(_action.StoreFilter, watermark: "Store filter (optional)");
        store.TextChanged += (_, _) => _action.StoreFilter = store.Text;

        var minPrice = UiKit.Text(_action.MinPrice?.ToString(), watermark: "Min price (optional)");
        minPrice.TextChanged += (_, _) =>
            _action.MinPrice = decimal.TryParse(minPrice.Text, out var v) ? v : null;

        _body.Children.Add(UiKit.Form(
            UiKit.Row("Name", name),
            UiKit.Row("Trigger", trigger),
            UiKit.Row("Store filter", store),
            UiKit.Row("Min price", minPrice)));
    }

    private void BuildFilters()
    {
        var rows = new ListBox { Height = 160 };
        void Refresh() => rows.ItemsSource = _filters.Count == 0
            ? new List<string> { "(no filters — always runs)" }
            : _filters.Select(f => f.ToString()).ToList();
        Refresh();

        var field = UiKit.Combo(SmartActionFilter.Fields.ToList());
        var op = UiKit.Combo(SmartActionFilter.Operators.ToList());
        var value = UiKit.Text(watermark: "value");

        _body.Children.Add(UiKit.Section("Filters",
            rows,
            UiKit.Row("Field", field),
            UiKit.Row("Operator", op),
            UiKit.Row("Value", value),
            UiKit.Buttons(
                // R230: the buttons go through the bound commands instead of editing the list themselves
                UiKit.Button("New filter", () => AddFilter(new SmartActionFilter
                {
                    Field = field.SelectedItem as string ?? "store",
                    Operator = op.SelectedItem as string ?? "equals",
                    Value = value.Text ?? string.Empty,
                })),
                UiKit.Button("Delete", () => DeleteFilter(rows.SelectedIndex)))));
    }

    private void BuildActions()
    {
        var kind = UiKit.Combo(Enum.GetNames<SmartActionKind>(), (int)_action.Kind);
        kind.SelectionChanged += (_, _) =>
            _action.Kind = (SmartActionKind)Math.Max(0, kind.SelectedIndex);

        var target = UiKit.Text(_action.Target, watermark: "webhook url / notification text");
        target.TextChanged += (_, _) => _action.Target = target.Text ?? string.Empty;

        var runOnce = UiKit.Check("Run once", _action.RunOnce);
        runOnce.IsCheckedChanged += (_, _) => _action.RunOnce = runOnce.IsChecked == true;

        var interval = UiKit.Text(_action.RunInterval?.ToString(), watermark: "00:00:30");
        interval.TextChanged += (_, _) =>
            _action.RunInterval = TimeSpan.TryParse(interval.Text, out var v) ? v : null;

        var notify = UiKit.Check("Notify", _action.Notifications);
        notify.IsCheckedChanged += (_, _) => _action.Notifications = notify.IsChecked == true;

        var enabled = UiKit.Check("Enabled", _action.Enabled);
        enabled.IsCheckedChanged += (_, _) => _action.Enabled = enabled.IsChecked == true;

        _body.Children.Add(UiKit.Form(
            UiKit.Row("Action kind", kind),
            UiKit.Row("Target", target),
            UiKit.Row("Run once", runOnce),
            UiKit.Row("Run interval", interval),
            UiKit.Row("Notify", notify),
            UiKit.Row("Enabled", enabled),
            UiKit.Caption($"Filters attached: {_filters.Count}")));
    }

    public void SaveCore()
    {
        try
        {
            _action.Filters = _filters.ToList();
            if (!_services.Config.SmartActions.Actions.Contains(_action))
                _services.Config.SmartActions.Actions.Add(_action);

            _services.Config.Save();
            _status.Text = "Action saved.";
        }
        catch (Exception ex)
        {
            _status.Text = ex.Message;
        }
    }
}

/// <summary>
/// Action picker (Cybersole.Ui.Views.SmartActions.ActionsModal) — Title / InputFormat /
/// OutputFormat / SearchPlaceholder.
/// </summary>
public sealed class ActionsModal : Window
{
    /// <summary>Bound as <c>Add</c>: the same command the "Add" button carries.</summary>
    public ICommand Add { get; }


    private readonly ComboBox _picker;
    private readonly ListBox _preview = new() { Height = 140 };

    public ActionsModal(IEnumerable<SmartAction> actions)
    {
        Title = "Actions";
        Width = 520;
        Height = 420;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var list = actions.ToList();
        _picker = UiKit.Combo(list.Select(a => a.Name).DefaultIfEmpty("(none)").ToList(), 0, width: 460);
        _picker.SelectionChanged += (_, _) => Preview(list);

        var addButton = new Button
        {
            Content = "Add",
            Command = new RelayCommand(() =>
            {
                Accepted = true;
                Close();
            }),
        };
        Add = addButton.Command!;

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title("Actions"),
                UiKit.Row("Pick", _picker),
                UiKit.Row("Preview", _preview),
                UiKit.Buttons(
                    addButton,
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
            },
        };

        Preview(list);
    }

    public bool Accepted { get; private set; }

    public string SelectedAction => _picker.SelectedItem as string ?? string.Empty;

    private void Preview(List<SmartAction> list)
    {
        var index = _picker.SelectedIndex;
        if (index < 0 || index >= list.Count)
        {
            _preview.ItemsSource = new List<string> { "(no actions)" };
            return;
        }

        var a = list[index];
        _preview.ItemsSource = new List<string>
        {
            "trigger: " + a.Trigger,
            "kind: " + a.Kind,
            "target: " + a.Target,
            "filters: " + a.Filters.Count,
            "enabled: " + a.Enabled,
        };
    }
}

/// <summary>
/// Run history (Cybersole.Ui.Views.SmartActions.HistoryWindow) — filter All / Completed /
/// Failed over the engine's execution log.
/// </summary>
public sealed class HistoryWindow : Window
{
    /// <summary>Which history rows are shown (bound as <c>Filter</c>): All / Completed / Failed.</summary>
    public string Filter
    {
        get => _filter.SelectedItem as string ?? "All";
        set
        {
            if (string.IsNullOrEmpty(value)) return;
            _filter.SelectedItem = value;
        }
    }

    // ------------------------------------------------ copy from the image's locale (R421)
    //
    // Verbatim from the string table; same table shape as the other pages.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["Empty"] = "No history entries",   // HistoryWindow.Empty
        ["EmptyNoMatch"] = "No recent runs match your filter!",   // HistoryWindow.Empty.NoMatch
        ["EmptyNoRuns"] = "Smart Action hasn't been triggered yet",   // HistoryWindow.Empty.NoRuns
        ["EmptySubtitle"] = "Run history will appear here",   // HistoryWindow.Empty.Subtitle
        ["EmptyInput"] = "Empty input",   // HistoryWindow.EmptyInput
        ["HoverTip"] = "Hover over each step to view more details",   // HistoryWindow.HoverTip
        ["ResultSuccess"] = "The Smart Action completed successfully!",   // HistoryWindow.Result.Success
        ["Clear"] = "Clear History",   // HistoryWindow.Clear
        ["SearchPlaceholder"] = "Search history",   // HistoryWindow.SearchPlaceholder
    };

    /// <summary>One of the image's strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
    private readonly ListBox _rows = new() { Height = 300 };
    private readonly IReadOnlyList<SmartActionEngine.SmartActionExecution> _history;
    private readonly TextBlock _status = UiKit.Status();
    private readonly ComboBox _filter;

    /// <summary>
    /// Which smart action's history is on screen, or null for all of them (bound as <c>SmartAction</c>). Setting it filters the
    /// list; the window title follows <c>HistoryWindow.LogsFormat</c> — "{0} - Logs".
    /// </summary>
    public static string FormatLogsTitle(string? actionName) =>
        Cybersole.Ui.Localization.LocalizeHelpers.Format(
            "HistoryWindow.LogsFormat",
            Cybersole.Ui.Localization.LocalizeHelpers.Fallback(actionName, "All smart actions", translateFallbackKey: false));

    public SmartAction? SmartAction
    {
        get => _smartAction;
        set
        {
            _smartAction = value;
            Title = FormatLogsTitle(value?.Name);
            Render();
        }
    }

    /// <summary>Which of the two views is shown — "History" or "Logs" (bound as <c>View</c>).</summary>
    public string View
    {
        get => _view;
        set
        {
            _view = value;
            Render();
        }
    }

    /// <summary>Title format the image uses for this window (<c>HistoryWindow.LogsFormat</c>).</summary>
    public const string LocaleLogsFormat = "{0} - Logs";

    private SmartAction? _smartAction;
    private string _view = "History";

    /// <summary>Closes the history window (bound as <c>Exit</c>).</summary>
    private void ExitCore() => Close();

    /// <summary>Minimises the history window (bound as <c>Minimise</c>).</summary>
    private void MinimiseCore() => WindowState = WindowState.Minimized;

    // R498: bound names for no-arg window actions (each already existed as a method).
    /// <summary>Bound as <c>Exit</c>; behaviour unchanged (was a method).</summary>
    public ICommand Exit { get; }

    /// <summary>Bound as <c>Minimise</c>; behaviour unchanged (was a method).</summary>
    public ICommand Minimise { get; }

    /// <summary>Bound as <c>ShowAll</c>; behaviour unchanged (was a method).</summary>
    public ICommand ShowAll { get; }

    public HistoryWindow(AppServices services)
    {
        Exit = new RelayCommand(ExitCore);
        Minimise = new RelayCommand(MinimiseCore);
        ShowAll = new RelayCommand(ShowAllCore);

        Title = "Smart action history";
        Width = 720;
        Height = 520;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        _history = services.SmartActions.History;
        _filter = UiKit.Combo(new[] { "All", "Completed", "Failed" }, 0, _ => Render(), width: 180);
        _filter.SelectionChanged += (_, _) => Render();

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title("History"),
                UiKit.Row("Filter", _filter),
                _rows,
                UiKit.Buttons(new Button { Content = "Close", Command = new RelayCommand(Close) }),
                _status,
            },
        };

        Render();
    }

    /// <summary>
    /// Shows every row, whatever the filter says (bound as <c>ShowAll</c>). The original's history window binds it,
    /// and the replica had only the combo.
    /// </summary>
    private void ShowAllCore()
    {
        _filter.SelectedIndex = 0;   // "All"; the SelectionChanged handler re-renders
        Render();
    }

    /// <summary>The rows currently on screen, for callers and tests.</summary>
    public IReadOnlyList<object> Rows => _rows.ItemsSource?.Cast<object>().ToList() ?? new List<object>();

    private void Render()
    {
        IEnumerable<SmartActionEngine.SmartActionExecution> rows = _history;

        rows = _filter.SelectedIndex switch
        {
            1 => rows.Where(r => r.Executed),
            2 => rows.Where(r => !r.Executed),
            _ => rows,
        };

        var list = rows.ToList();
        _rows.ItemsSource = list.Count == 0
            ? new List<string> { "(no runs yet)" }
            : list.Select(r => $"{r.At:HH:mm:ss}  {r.RuleName}  {r.Trigger}  {(r.Executed ? "ok" : "fail")}  {r.Error}")
                .ToList();

        _status.Text = $"{list.Count} of {_history.Count} run(s).";
    }
}

/// <summary>
/// Template picker (Cybersole.Ui.Views.SmartActions.TemplateView) — FromScratch /
/// FromTemplate / Blank.
/// </summary>
public sealed class TemplateView : UserControl
{
    private readonly AppServices _services;
    private readonly TextBlock _status = UiKit.Status();

    public TemplateView(AppServices services)
    {
        _services = services;

        var list = new ListBox
        {
            Height = 240,
            ItemsSource = services.Config.SmartActions.Actions.Select(a => a.Name).DefaultIfEmpty("(no templates)").ToList(),
        };

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("New smart action"),
                UiKit.Caption("Start blank or seed from an existing action."),
                list,
                UiKit.Buttons(
                    UiKit.Button("From scratch", () => OpenEditor()),
                    UiKit.Button("From template", () => OpenEditor()),
                    UiKit.Button("Blank", () => OpenEditor())),
                _status,
            },
        };
    }

    /// <summary>
    /// Open the action editor.
    ///
    /// The three buttons above used to write a status line and nothing else — "Starting from a
    /// blank action." with no editor, "Seeding from X" with no seed. SmartActionEditorWindow
    /// existed the whole time. Same defect as TasksViews (rounds 97/99) and the Profiles page
    /// (round 100).
    ///
    /// "From template" and "Blank" both open the same editor with no action attached, because
    /// SmartAction has no template field to seed from: the picker lists existing actions but the
    /// model cannot express "copy of". Naming that here is better than implying it works.
    /// </summary>
    private void OpenEditor()
    {
        var owner = TopLevel.GetTopLevel(this) as Window;
        if (owner is null)
        {
            _status.Text = "No owner window — cannot open the editor.";
            return;
        }

        var editor = new SmartActionEditorWindow(_services);
        editor.Closed += (_, _) => { _services.Config.Save(); };
        _ = editor.ShowDialog(owner);
        _status.Text = "Smart-action editor opened.";
    }
}
/// <summary>
/// Publish template (Cybersole.Ui.Views.SmartActions.PublishTemplateModal) — Close / Groups.
/// </summary>
public sealed class PublishTemplateModal : Window
{
    private readonly ListBox _groups = new() { Height = 180 };
    private readonly TextBlock _status = UiKit.Status();

    /// <summary>The task groups a template can be published to (bound as <c>Groups</c>). One entry when there are none.</summary>
    public IReadOnlyList<string> Groups => _groups.ItemsSource?.Cast<string>().ToList() ?? new List<string>();

    public PublishTemplateModal(AppServices services, SmartAction? action = null)
    {
        Title = PublishTemplateHeader;
        Width = 480;
        Height = 460;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        _groups.ItemsSource = services.Config.TaskGroups.Select(g => g.Name).DefaultIfEmpty(DefaultGroup).ToList();
        _groups.SelectedIndex = 0;

        var title = UiKit.Text(action?.Name, watermark: "Template title");
        var description = UiKit.Text(null, watermark: "What does this template do?");

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 8,
            Children =
            {
                UiKit.Title(PublishTemplateHeader),
                UiKit.Row("Title", title),
                UiKit.Row("Description", description),
                UiKit.Row("Group", _groups),
                _status,
                UiKit.Buttons(
                    new Button
                    {
                        Content = "Publish",
                        Command = new RelayCommand(() =>
                        {
                            // PublishTemplate.Error.NoTitle: "You must enter a title". The dialog
                            // had this string available and never checked it, so an empty title
                            // published an unnamed template.
                            var name = title.Text?.Trim();
                            if (string.IsNullOrEmpty(name))
                            {
                                _status.Text = "You must enter a title";
                                title.Focus();
                                return;
                            }

                            services.Config.SmartActions.Templates.Add(new PublishedTemplate
                            {
                                Title = name,
                                Description = description.Text?.Trim() ?? string.Empty,
                                Group = _groups.SelectedItem as string ?? DefaultGroup,
                                SourceActionId = action?.Id,
                            });
                            services.Config.Save();

                            Published = true;
                            Close();
                        }),
                    },
                    new Button { Content = "Close", Command = new RelayCommand(Close) }),
            },
        };
    }

    /// <summary>The window caption and the section heading, from PublishTemplate.Header.</summary>
    public const string PublishTemplateHeader = "Publish Template";

    private const string DefaultGroup = "Group 1";

    public bool Published { get; private set; }
}

/// <summary>
/// Action settings (Cybersole.Ui.Views.SmartActions.SmartActionSettings) — Name / Enabled /
/// RunOnce / RunInterval / Notifications / Webhooks / Delete.
/// </summary>
public sealed class SmartActionSettingsView : UserControl
{
    private readonly AppServices _services;
    private readonly SmartAction _action;
    private readonly TextBlock _status = UiKit.Status();

    public SmartActionSettingsView(AppServices services, SmartAction? action = null)
    {
        _services = services;
        _action = action ?? new SmartAction { Name = "Action" };

        var name = UiKit.Text(_action.Name, watermark: "Action name");
        name.TextChanged += (_, _) => _action.Name = name.Text ?? _action.Name;

        var enabled = UiKit.Check("Enabled", _action.Enabled);
        enabled.IsCheckedChanged += (_, _) => _action.Enabled = enabled.IsChecked == true;

        var runOnce = UiKit.Check("Run once", _action.RunOnce);
        ToolTip.SetTip(runOnce, "If enabled, this smart action will automatically disable itself after running");
        runOnce.IsCheckedChanged += (_, _) => _action.RunOnce = runOnce.IsChecked == true;

        var interval = UiKit.Text(_action.RunInterval?.ToString(), watermark: "00:00:30");
        ToolTip.SetTip(interval, "The amount of time that must have elapsed before the smart action may run again");
        interval.TextChanged += (_, _) =>
            _action.RunInterval = TimeSpan.TryParse(interval.Text, out var v) ? v : null;

        var notifications = UiKit.Check("Notifications", _action.Notifications);
        ToolTip.SetTip(notifications, "Whether to send notifications when this smart action runs. You can configure or disable global notifications in settings.");
        notifications.IsCheckedChanged += (_, _) => _action.Notifications = notifications.IsChecked == true;

        var webhooks = new ListBox
        {
            Height = 120,
            ItemsSource = _services.Config.Settings.Webhooks
                .Select(w => w.Name ?? w.Url)
                .DefaultIfEmpty("(none configured)")
                .ToList(),
        };
        ToolTip.SetTip(webhooks, "Whether to send webhook notifications when this smart action runs.");

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Title("Action settings"),
            UiKit.Section("Behaviour",
                UiKit.Row("Name", name),
                UiKit.Row("Enabled", enabled),
                UiKit.Row("Run once", runOnce),
                UiKit.Row("Run interval", interval),
                UiKit.Row("Notifications", notifications)),
            UiKit.Section("Webhooks", webhooks),
            UiKit.Buttons(
                UiKit.Button("Save", () =>
                {
                    try
                    {
                        if (!_services.Config.SmartActions.Actions.Contains(_action))
                            _services.Config.SmartActions.Actions.Add(_action);
                        _services.Config.Save();
                        _status.Text = "Saved.";
                    }
                    catch (Exception ex)
                    {
                        _status.Text = ex.Message;
                    }
                }),
                UiKit.Button("Delete", () =>
                {
                    _services.Config.SmartActions.Actions.Remove(_action);
                    _services.Config.Save();
                    _status.Text = "Deleted.";
                })),
            _status));
    }
}
