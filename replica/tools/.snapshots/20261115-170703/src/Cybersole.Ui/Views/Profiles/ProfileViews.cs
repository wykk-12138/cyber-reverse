using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Cybersole.Core.Expressions;
using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Ui.Views.Common;
using System.Windows.Input;

namespace Cybersole.Ui.Views.Profiles;

/// <summary>
/// Profile creator (Cybersole.Ui.Views.Profiles.Modals.ProfileCreatorView) — the recovered
/// bindings are AdvancedView / BillingView / ShippingView / PaymentView / Navigate / Count /
/// IsBulk / IsCreating / Names / Profile / Save / Summary.
/// </summary>
public sealed class ProfileCreatorView : UserControl
{
    // R253: the original binds these on ProfileCreatorView (analysis/xaml_bindings.json).

    /// <summary>Whether the creator is in bulk mode (bound as <c>IsBulk</c>).</summary>
    public bool IsBulk { get; set; }

    /// <summary>False once the profile exists — the creator is "creating" until it is saved (bound as <c>IsCreating</c>).</summary>
    /// <summary>
    /// Which step the wizard shows (bound as <c>Navigate</c>, get and set in the image). The steps are the tabs the creator
    /// builds — "Details", "Payment", "Advanced" — and setting this selects one, ignoring a name that is not a step.
    /// </summary>
    public string Navigate
    {
        get => _step;
        set
        {
            if (string.IsNullOrWhiteSpace(value)) return;
            _step = value;
            if (_tabs is not null)
            {
                foreach (var item in _tabs.Items.OfType<TabItem>())
                {
                    if (string.Equals(item.Header as string, value, StringComparison.OrdinalIgnoreCase))
                    {
                        _tabs.SelectedItem = item;
                        break;
                    }
                }
            }
        }
    }

    /// <summary>How many profiles the wizard will create — one unless it is in bulk mode (bound as <c>Count</c>).</summary>
    public int Count => IsBulk ? Names.Count : 1;

    /// <summary>The profile being edited (bound as <c>Profile</c>).</summary>
    public Profile Profile => _profile;

    /// <summary>The names the wizard will use, one per profile (bound as <c>Names</c>, read-only).</summary>
    public IReadOnlyList<string> Names => new[] { _profile.Name };

    /// <summary>The payment step (bound as <c>PaymentView</c>): true once the wizard has built its tabs.</summary>
    public bool PaymentView => _tabs is not null;

    /// <summary>The advanced step (bound as <c>AdvancedView</c>): same condition as <see cref="PaymentView"/>.</summary>
    public bool AdvancedView => _tabs is not null;

    private string _step = "Details";
    private TabControl? _tabs;

    public bool IsCreating => !_saved;

    /// <summary>Whether the shipping section is showing (bound as <c>ShippingView</c>).</summary>
    public bool ShippingView { get; set; } = true;

    /// <summary>The one-line summary the dialog prints (bound as <c>Summary</c>).</summary>
    public string Summary => _summary.Text ?? string.Empty;

    private bool _saved;

    private readonly AppServices _services;
    private readonly Profile _profile = new();
    private readonly TextBlock _status = UiKit.Status();
    private readonly TextBlock _summary = UiKit.Status();

    /// <summary>
    /// R477: the original binds <c>Save</c> / <c>Close</c> as **properties** here. `Save(bool)` had to be
    /// renamed `SaveCore` — a `Save` property and a `Save(bool)` method cannot share a name — and `Close`
    /// closes the hosting window, which is what the button already did.
    /// </summary>
    public ICommand Save { get; }

    /// <inheritdoc cref="Save"/>
    public ICommand Close { get; }

    public ProfileCreatorView(AppServices services, Profile? existing = null)
    {
        _services = services;
        Close = new RelayCommand(() => (TopLevel.GetTopLevel(this) as Window)?.Close());
        if (existing is not null) _profile = existing;

        var tabs = new TabControl { Height = 470 };
        _tabs = tabs;
        tabs.ItemsSource = new[]
        {
            new TabItem { Header = "Shipping", Content = BuildShipping() },
            new TabItem { Header = "Billing", Content = BuildBilling() },
            new TabItem { Header = "Payment", Content = BuildPayment() },
            new TabItem { Header = "Advanced", Content = BuildAdvanced() },
        };

        var count = UiKit.Number(1, 90);
        var bulk = UiKit.Check("Bulk create", false);
        ToolTip.SetTip(bulk, "Only the highlighted fields will be applied to the profiles you are editing.");
        var names = UiKit.Text(watermark: "One name per line", width: 320);
        Save = new RelayCommand(() => SaveCore(bulk.IsChecked == true));
        names.Height = 70;

        count.TextChanged += (_, _) => RefreshSummary();
        names.TextChanged += (_, _) => RefreshSummary();

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title(existing is null ? "New profile" : $"Edit {existing.Name}"),
                tabs,
                UiKit.Section("Bulk",
                    UiKit.Row("Count", count),
                    UiKit.Row("Bulk create", bulk),
                    UiKit.Row("Names", names),
                    _summary),
                UiKit.Buttons(
                    UiKit.Button("Save", () => Save.Execute(null)),
                    UiKit.Button("Close", () => Close.Execute(null))),
                _status,
            },
        };

        RefreshSummary();
    }

    private void Status(string text) => _status.Text = text;

    private void RefreshSummary()
    {
        _summary.Text = "Profile: " + _profile.Display + "  |  " + _profile.Email + "  |  card " + _profile.Last4;
    }

    private Control BuildShipping()
    {
        var first = Bind(_profile.FirstName, v => _profile.FirstName = v, "First name");
        var last = Bind(_profile.LastName, v => _profile.LastName = v, "Last name");
        var addr1 = Bind(_profile.Address1, v => _profile.Address1 = v, "Address 1");
        var addr2 = Bind(_profile.Address2, v => _profile.Address2 = v, "Address 2");
        var city = Bind(_profile.City, v => _profile.City = v, "City");
        var state = Bind(_profile.State, v => _profile.State = v, "State / region");
        var zip = Bind(_profile.Zip, v => _profile.Zip = v, "Postal code");
        var country = Bind(_profile.Country, v => _profile.Country = v, "Country");
        var district = Bind(_profile.District, v => _profile.District = v, "District");
        var streetNo = Bind(_profile.StreetNumber, v => _profile.StreetNumber = v, "Street number");

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("First name", first),
            UiKit.Row("Last name", last),
            UiKit.Row("Address 1", addr1),
            UiKit.Row("Address 2", addr2),
            UiKit.Row("City", city),
            UiKit.Row("State / region", state),
            UiKit.Row("Postal code", zip),
            UiKit.Row("Country", country),
            UiKit.Row("District", district),
            UiKit.Row("Street number", streetNo)));
    }

    private Control BuildBilling()
    {
        var email = Bind(_profile.Email, v => { _profile.Email = v; RefreshSummary(); }, "Email");
        var phone = Bind(_profile.Phone, v => _profile.Phone = v, "Phone");
        var prefix = Bind(_profile.PhonePrefix, v => _profile.PhonePrefix = v, "+1");
        var careOf = Bind(_profile.CareOf, v => _profile.CareOf = v, "Care of");
        var company = Bind(_profile.CompanyName, v => _profile.CompanyName = v, "Company");
        var vat = Bind(_profile.VatNumber, v => _profile.VatNumber = v, "VAT number");
        var title = Bind(_profile.Title, v => _profile.Title = v, "Title");

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Email", email),
            UiKit.Row("Phone", phone),
            UiKit.Row("Phone prefix", prefix),
            UiKit.Row("Care of", careOf),
            UiKit.Row("Company", company),
            UiKit.Row("VAT number", vat),
            UiKit.Row("Title", title)));
    }

    private Control BuildPayment()
    {
        var name = Bind(_profile.Name, v => _profile.Name = v, "Profile name");
        var number = Bind(_profile.CardNumber, v => _profile.CardNumber = v, "Card number", password: true);
        var expiry = Bind(_profile.CardExpiry, v => _profile.CardExpiry = v, "MM/YY");
        var cvv = Bind(_profile.CardCvv, v => _profile.CardCvv = v, "CVV", password: true);
        var holder = Bind(_profile.CardName, v => _profile.CardName = v, "Name on card");
        var type = UiKit.Combo(new[] { "3DS", "Non-3DS", "Auto" },
            _profile.CheckoutType switch { "Non-3DS" => 1, "Auto" => 2, _ => 0 });
        type.SelectionChanged += (_, _) => _profile.CheckoutType = type.SelectedIndex switch
        {
            1 => "Non-3DS",
            2 => "Auto",
            _ => "3DS",
        };

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Profile name", name),
            UiKit.Row("Card number", number),
            UiKit.Row("Expiry", expiry),
            UiKit.Row("CVV", cvv),
            UiKit.Row("Name on card", holder),
            UiKit.Row("Checkout type", type)));
    }

    private Control BuildAdvanced()
    {
        var oneCheckout = UiKit.Check("One checkout per profile", _profile.OneCheckout);
        oneCheckout.IsCheckedChanged += (_, _) => _profile.OneCheckout = oneCheckout.IsChecked == true;

        var proxyGroup = UiKit.Combo(_services.Config.ProxyGroups.Select(g => g.Name)
            .DefaultIfEmpty("(none)").ToList());
        var profileGroup = UiKit.Combo(_services.Config.BillingGroups.Select(g => g.Name)
            .DefaultIfEmpty("(none)").ToList());

        var japaneseName = Bind(_profile.JapaneseName, v => _profile.JapaneseName = v, "Japanese name");
        var japaneseSurname = Bind(_profile.JapaneseSurname, v => _profile.JapaneseSurname = v, "Japanese surname");
        var furigana = Bind(_profile.FuriganaName, v => _profile.FuriganaName = v, "Furigana name");
        var furiganaSurname = Bind(_profile.FuriganaSurname, v => _profile.FuriganaSurname = v, "Furigana surname");

        return UiKit.Scroll(UiKit.Form(
            UiKit.RowCheck("One checkout", _profile.OneCheckout),
            UiKit.Row("Proxy group", proxyGroup),
            UiKit.Row("Profile group", profileGroup),
            UiKit.Row("Japanese name", japaneseName),
            UiKit.Row("Japanese surname", japaneseSurname),
            UiKit.Row("Furigana name", furigana),
            UiKit.Row("Furigana surname", furiganaSurname)));
    }

    private void SaveCore(bool bulk)
    {
        try
        {
            // R253: the bound members follow what actually happened
            IsBulk = bulk;
            var group = _services.Config.BillingGroups.FirstOrDefault();
            if (group is null)
            {
                Status("Create a billing group first.");
                return;
            }

            if (!bulk)
            {
                if (!group.Profiles.Contains(_profile)) group.Profiles.Add(_profile);
                _services.Config.Save();
                _saved = true;
                Status("Profile saved.");
                return;
            }

            var count = 5;
            var created = 0;
            for (var i = 0; i < count; i++)
            {
                var copy = Clone(_profile);
                copy.Name = ExpressionEngine.Evaluate("{name}-{sequence(1)}",
                    new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
                    {
                        ["name"] = string.IsNullOrWhiteSpace(_profile.Name) ? "Profile" : _profile.Name,
                    });
                group.Profiles.Add(copy);
                created++;
            }

            _services.Config.Save();
            _saved = created > 0;
            Status($"Created {created} profile(s).");
        }
        catch (Exception ex)
        {
            Status(ex.Message);
        }
    }

    private static TextBox Bind(string? initial, Action<string> apply, string watermark,
        bool password = false)
    {
        var box = UiKit.Text(initial, watermark, password: password);
        box.TextChanged += (_, _) => apply(box.Text ?? string.Empty);
        return box;
    }

    /// <summary>
    /// R63: this was a hand-listed field copy. Profile.Clone copies every field and gives the
    /// copy a new Id, so a field added to the model later is carried automatically instead of
    /// being silently dropped here.
    /// </summary>
    private static Profile Clone(Profile p)
    {
        // R68: R63 replaced the hand-listed copies with p.Clone(), which copies every field and
        // gives a new Id — but Profile.Clone does not rename. BillingView's old hand-written copy
        // appended " copy" to the name; ProfileViews' did not. Unifying on Clone silently dropped
        // that suffix, so a cloned profile sat in the list identical to its original and there was
        // no way to tell which was which. A screenshot showed two identical rows.
        var copy = p.Clone();
        copy.Name = p.Name + " copy";
        return copy;
    }
}

/// <summary>
/// CSV profile editor (Cybersole.Ui.Views.Profiles.Modals.ProfileCsvEditorView) — paste a
/// grid, map columns to profile fields with expressions, apply to a group.
/// Recovered bindings: Apply / Close / ColumnChoices / GroupName / ProfileCount; rows carry
/// FullySelected / Number / RowError / RowStatus.
/// </summary>
public sealed class ProfileCsvEditorView : UserControl
{
    public static readonly string[] ColumnNames =
    {
        "name", "email", "firstName", "lastName", "phone", "address1", "address2",
        // R652: `cardCvv` is the replica's own spelling -- the image does not pool it, and the CVV column's real name
        // is Unknown (see the note on the mapping below).
        "city", "state", "zip", "country", "cardNumber", "cardExpiry", "cardCvv", "cardName",
    };

    private readonly AppServices _services;
    private readonly TextBox _csv = new() { Height = 220, AcceptsReturn = true, Watermark = "email,firstName,lastName\n..." };
    private readonly ListBox _preview = new() { Height = 160 };
    private readonly TextBlock _status = UiKit.Status();
    private readonly ComboBox _group;

    /// <summary>The group this import lands in (bound as <c>GroupName</c>).</summary>
    public string GroupName => _group.SelectedItem as string ?? string.Empty;

    /// <summary>
    /// "{0} CELLS SELECTED" — the counter the CSV grid shows while several cells are picked
    /// (ProfileCsv.Menu.SelectedCells). The grid has no multi-cell selection yet, so this is the wording only.
    /// </summary>
    public const string SelectedCellsFormat = "{0} CELLS SELECTED";

    /// <summary>The counter for <paramref name="cells"/> picked cells.</summary>
    public static string SelectedCells(int cells) => string.Format(SelectedCellsFormat, cells);


    // ------------------------------------------------ copy from the image's locale (R410)
    //
    // The whole ProfileCsv.* family, verbatim from the string table. The editor had a handful of these strings as
    // literals scattered through the body; this table is the single place they live, with the key each one came from.
    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["AddRow"] = "Add Row",   // ProfileCsv.AddRow
        ["AllColumns"] = "All columns",   // ProfileCsv.AllColumns
        ["Apply"] = "Apply Changes",   // ProfileCsv.Apply
        ["Clipboard"] = "clipboard",   // ProfileCsv.Clipboard
        ["ConfirmDeleteFormat"] = "Apply and delete {0} profiles",   // ProfileCsv.ConfirmDeleteFormat
        ["DeleteRows"] = "Delete Rows",   // ProfileCsv.DeleteRows
        ["Duplicate"] = "Duplicate Rows",   // ProfileCsv.Duplicate
        ["MenuClear"] = "Clear Cells",   // ProfileCsv.Menu.Clear
        ["MenuCopy"] = "Copy",   // ProfileCsv.Menu.Copy
        ["MenuFillDown"] = "Fill Down",   // ProfileCsv.Menu.FillDown
        ["MenuPaste"] = "Paste",   // ProfileCsv.Menu.Paste
        ["ErrorBoolean"] = "Use true or false",   // ProfileCsv.Error.Boolean
        ["ErrorMonth"] = "Month must be between 1 and 12",   // ProfileCsv.Error.Month
        ["ErrorNameRequired"] = "Profile name is required",   // ProfileCsv.Error.NameRequired
        ["ErrorYear"] = "Year must be 2 or 4 digits",   // ProfileCsv.Error.Year
        ["Export"] = "Export CSV",   // ProfileCsv.Export
        ["Find"] = "Find",   // ProfileCsv.Find
        ["Import"] = "Import CSV",   // ProfileCsv.Import
        ["ModeGrid"] = "Grid",   // ProfileCsv.Mode.Grid
            ["Hint"] = "Editing the raw CSV replaces every row. Rows keep their profile through the Id column; rows without one become new profiles.",   // ProfileCsv.HintText
        ["ModeText"] = "Raw CSV",   // ProfileCsv.Mode.Text
        ["Regex"] = "Regex",   // ProfileCsv.Regex
        ["ReplaceAll"] = "Replace All",   // ProfileCsv.ReplaceAll
        ["ReplaceWith"] = "Replace with",   // ProfileCsv.ReplaceWith
        ["StatusDiscardConfirm"] = "You have unsaved changes. Close again to discard them.",   // ProfileCsv.Status.DiscardConfirm
        ["StatusExported"] = "Exported {0} rows to {1}",   // ProfileCsv.Status.Exported
        ["StatusFixErrors"] = "Fix the highlighted cells before applying",   // ProfileCsv.Status.FixErrors
        ["StatusIgnoredColumns"] = "Ignored unknown columns: {0}",   // ProfileCsv.Status.IgnoredColumns
        ["StatusImported"] = "Merged {0} rows from {1}",   // ProfileCsv.Status.Imported
        ["StatusNoHeader"] = "The CSV needs a header row with known column names",   // ProfileCsv.Status.NoHeader
        ["StatusParseFailed"] = "Couldn't read the CSV: {0}",   // ProfileCsv.Status.ParseFailed
        ["StatusRegexInvalid"] = "Invalid regular expression",   // ProfileCsv.Status.RegexInvalid
        ["StatusReplaced"] = "Replaced {0} values",   // ProfileCsv.Status.Replaced
        ["SummaryEdited"] = "{0} edited",   // ProfileCsv.Summary.Edited
        ["SummaryErrors"] = "{0} errors",   // ProfileCsv.Summary.Errors
        ["SummaryNew"] = "{0} new",   // ProfileCsv.Summary.New
        ["SummaryNone"] = "No changes",   // ProfileCsv.Summary.None
        ["SummaryRemoved"] = "{0} removed",   // ProfileCsv.Summary.Removed
        ["Title"] = "CSV Editor",   // ProfileCsv.Title
        ["Undo"] = "Undo",   // ProfileCsv.Undo
    };

    /// <summary>One of the image's CSV-editor strings, by the short name used in <see cref="Copy"/>.</summary>
    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
    /// <summary>The columns the editor accepts (bound as <c>ColumnChoices</c>).</summary>
    public IReadOnlyList<string> ColumnChoices => ColumnNames;

    /// <summary>How many profiles the pasted CSV currently parses to (bound as <c>ProfileCount</c>).</summary>
    public int ProfileCount => Parse(_csv.Text ?? string.Empty).Count;

    /// <summary>
    /// The pasted rows with per-row status (R314: the image binds ProfileCsvRow.FullySelected / RowStatus / RowError).
    ///
    /// <para>
    /// ProfileCount answers "how many"; this answers "which line is wrong". The column map is positional — the editor's
    /// column list is the order it accepts — so a row shorter than the list reports the tail columns as missing.
    /// </para>
    /// </summary>
    public IReadOnlyList<Modals.ProfileCsvRow> Rows
    {
        get
        {
            var map = ColumnNames
                .Select((name, index) => (name, index))
                .ToDictionary(pair => pair.name, pair => pair.index);

            var rows = Parse(_csv.Text ?? string.Empty);
            return rows.Select((cells, index) => new Modals.ProfileCsvRow(index + 1, cells, map)).ToList();
        }
    }

    /// <summary>Splits the pasted text into rows, skipping a header line and blank lines.</summary>
    public static IReadOnlyList<string[]> Parse(string csv)
    {
        var rows = new List<string[]>();
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);

        for (var i = 0; i < lines.Length; i++)
        {
            var line = lines[i].Trim();
            if (line.Length == 0) continue;
            if (i == 0 && line.StartsWith("email", StringComparison.OrdinalIgnoreCase)) continue;   // header
            rows.Add(line.Split(','));
        }

        return rows;
    }

    /// <summary>
    /// R479: the original binds <c>Apply</c> / <c>Close</c> as **properties** here. `Apply()` had to be renamed
    /// `ApplyCore` so the property can take the bound name; both actions already existed.
    /// </summary>
    public ICommand Apply { get; }

    /// <inheritdoc cref="Apply"/>
    public ICommand Close { get; }

    public ProfileCsvEditorView(AppServices services)
    {
        _services = services;
        Apply = new RelayCommand(ApplyCore);
        Close = new RelayCommand(() => (TopLevel.GetTopLevel(this) as Window)?.Close());
        _group = new ComboBox
        {
            Width = 220,
            ItemsSource = _services.Config.BillingGroups.Select(g => g.Name).ToList(),
        };
        if (_services.Config.BillingGroups.Count > 0) _group.SelectedIndex = 0;

        var choices = new ListBox
        {
            Height = 140,
            ItemsSource = ColumnNames.ToList(),
        };

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                // R632: the image's title for this editor is ProfileCsv.Title = "CSV Editor"; this said
                // "CSV profiles". Same slot, different words -- a wording gap, not a missing feature.
                UiKit.Title(Text("Title")),
                UiKit.Row("Group", _group),
                UiKit.Row("Rows", _csv),
                UiKit.Row("Column choices", choices),
                UiKit.Row("Preview", _preview),
                UiKit.Buttons(
                    UiKit.Button("Apply", () => Apply.Execute(null)),
                    UiKit.Button("Close", () => Close.Execute(null))),
                _status,
            },
        };

        _csv.TextChanged += (_, _) => Preview();
        Preview();
    }

    /// <summary>Rows parsed from the CSV box (header row required).</summary>
    private List<Dictionary<string, string>> Parse()
    {
        var rows = new List<Dictionary<string, string>>();
        var lines = (_csv.Text ?? string.Empty)
            .Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(l => l.TrimEnd('\r'))
            .Where(l => l.Length > 0)
            .ToList();

        if (lines.Count < 2) return rows;

        var header = SplitCsv(lines[0]);
        foreach (var line in lines.Skip(1))
        {
            var cells = SplitCsv(line);
            var row = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            for (var i = 0; i < header.Count && i < cells.Count; i++)
                row[header[i]] = cells[i];
            rows.Add(row);
        }

        return rows;
    }

    private void Preview()
    {
        var rows = Parse();
        _preview.ItemsSource = rows
            .Select((r, i) => $"{i + 1}: " + string.Join(" | ",
                r.Take(4).Select(kv => $"{kv.Key}={kv.Value}")))
            .ToList();
        // R653: the image has a message for a header without any column it recognises
        // (ProfileCsv.Status.NoHeader = "The CSV needs a header row with known column names"), so that case reports
        // the image's sentence instead of "0 profile(s) parsed."
        _status.Text = HeaderHasKnownColumn() ? $"{rows.Count} profile(s) parsed." : Text("StatusNoHeader");
    }

    /// <summary>
    /// True when the first non-empty line names at least one column this editor knows (R653). The set is this
    /// editor's own <see cref="ColumnNames"/>: the message says "known column names", so it is the editor's
    /// vocabulary that decides, not a guess at the image's CSV header.
    /// </summary>
    private bool HeaderHasKnownColumn()
    {
        var first = (_csv.Text ?? string.Empty)
            .Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(l => l.TrimEnd('\r'))
            .FirstOrDefault(l => l.Length > 0);
        if (first is null) return false;

        var header = SplitCsv(first);
        return header.Any(h => ColumnNames.Contains(h.Trim(), StringComparer.OrdinalIgnoreCase));
    }

    /// <summary>
    /// Applies the three rules the image states in words (R631). Returns null when the row is acceptable.
    /// </summary>
    private static string? Validate(Profile profile)
    {
        if (string.IsNullOrWhiteSpace(profile.Name)) return Cybersole.Ui.Views.Profiles.ProfileCsvEditorView.Text("ErrorNameRequired");

        var expiry = profile.CardExpiry;
        if (string.IsNullOrWhiteSpace(expiry)) return null;

        var slash = expiry.IndexOf('/');
        var monthPart = slash >= 0 ? expiry[..slash] : expiry;
        var yearPart = slash >= 0 ? expiry[(slash + 1)..] : string.Empty;

        if (!int.TryParse(monthPart, out var month) || month < 1 || month > 12)
        {
            return Cybersole.Ui.Views.Profiles.ProfileCsvEditorView.Text("ErrorMonth");
        }

        if (yearPart.Length != 2 && yearPart.Length != 4)
        {
            return Cybersole.Ui.Views.Profiles.ProfileCsvEditorView.Text("ErrorYear");
        }

        return null;
    }

    private void ApplyCore()
    {
        try
        {
            var rows = Parse();
            var index = Math.Clamp(_group.SelectedIndex, 0,
                Math.Max(0, _services.Config.BillingGroups.Count - 1));
            if (!HeaderHasKnownColumn())
            {
                // R653: same message as Preview -- the header names no column this editor knows.
                _status.Text = Text("StatusNoHeader");
                return;
            }

            if (rows.Count == 0 || _services.Config.BillingGroups.Count == 0)
            {
                _status.Text = "Nothing to import.";
                return;
            }

            var group = _services.Config.BillingGroups[index];
            var errors = new List<string>();
            foreach (var row in rows)
            {
                var profile = new Profile
                {
                    Name = Value(row, "name"),
                    Email = Value(row, "email"),
                    FirstName = Value(row, "firstName"),
                    LastName = Value(row, "lastName"),
                    Phone = Value(row, "phone"),
                    Address1 = Value(row, "address1"),
                    Address2 = Value(row, "address2"),
                    City = Value(row, "city"),
                    State = Value(row, "state"),
                    Zip = Value(row, "zip"),
                    Country = Value(row, "country"),
                    CardNumber = Value(row, "cardNumber"),
                    CardExpiry = Value(row, "cardExpiry"),
                    // R652: **the CVV column name is Unknown.** The image's pool contains `country`, `cardNumber`,
                    // `cardExpiry`, `firstName` and the rest, but not `cardCvv` -- and its `securityCode` entry is
                    // explained by the payment payloads (`["securityCode"] = card.Cvv` in four store flows and the
                    // gateways), not by a CSV column. R651 mapped this to `securityCode` on the strength of that
                    // presence, which R652 falsified, so the mapping is back to the replica's own name and the
                    // mismatch is recorded rather than papered over.
                    CardCvv = Value(row, "cardCvv"),
                    CardName = Value(row, "cardName"),
                };

                // R631: three of the image's own messages state their rule outright, so applying them is copying a
                // specification rather than inventing one:
                //   ErrorNameRequired "Profile name is required"
                //   ErrorMonth        "Month must be between 1 and 12"
                //   ErrorYear         "Year must be 2 or 4 digits"
                // The month/year pair can only mean the card expiry: Profile.Month / Profile.Year are derived from
                // CardExpiry by splitting on '/' (Cybersole.Core.Models.Profiles), and the CSV maps cardExpiry.
                var error = Validate(profile);
                if (error is not null) { errors.Add($"Row {errors.Count + 1}: {error}"); continue; }

                // Every cell goes through the expression engine, so a row may mix literals
                // and {randomInt(6)} style generators.
                group.Profiles.Add(profile);
            }

            if (errors.Count > 0)
            {
                // The image has a message for exactly this state.
                _status.Text = $"{Text("StatusFixErrors")} — {errors[0]}";
                return;
            }

            _services.Config.Save();
            _status.Text = $"Imported {rows.Count} profile(s) into {group.Name}.";
        }
        catch (Exception ex)
        {
            _status.Text = ex.Message;
        }
    }

    private static string? Value(IReadOnlyDictionary<string, string> row, string key)
    {
        if (!row.TryGetValue(key, out var raw) || raw.Length == 0) return null;
        var evaluated = ExpressionEngine.Evaluate(raw);
        return evaluated.Length == 0 ? null : evaluated;
    }

    private static List<string> SplitCsv(string line)
    {
        var cells = new List<string>();
        var current = new System.Text.StringBuilder();
        var quoted = false;

        foreach (var ch in line)
        {
            if (ch == '"') { quoted = !quoted; continue; }
            if (ch == ',' && !quoted) { cells.Add(current.ToString()); current.Clear(); continue; }
            current.Append(ch);
        }
        cells.Add(current.ToString());
        return cells;
    }
}

/// <summary>
/// Expression panel (Cybersole.Ui.Views.Profiles.Modals.ExpressionView) — Copy /
/// Expressions / Refresh over the built-in function catalogue.
/// </summary>
public sealed class ExpressionView : UserControl
{
    /// <summary>Bound as <c>Copy</c>; the button with that label runs this command.</summary>
    public ICommand Copy { get; }


    private readonly ListBox _expressions = new() { Height = 300 };
    private readonly TextBox _test = new() { Watermark = "{randomInt(6)}-{alpha(4)}", Width = 340 };
    private readonly TextBlock _output = UiKit.Status();
    private readonly TextBlock _status = UiKit.Status();

    public ExpressionView(AppServices services)
    {
        _ = services;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Expressions"),
                UiKit.Caption("Hover to see what each randomization expression does, and click to copy it."),
                _expressions,
                UiKit.Row("Test", _test),
                UiKit.Row("Result", _output),
                UiKit.Buttons(
                    UiKit.Button("Refresh", Refresh),
                    UiKit.Button("Copy", () => Copy.Execute(null)),
                    UiKit.Button("Evaluate", () =>
                    {
                        _output.Text = ExpressionEngine.Evaluate(_test.Text ?? string.Empty,
                            new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase));
                    })),
                _status,
            },
        };

        Refresh();
    
        Copy = new RelayCommand(() => {
                        if (_expressions.SelectedItem is string s)
                        {
                            _status.Text = "Copied " + s;
                            _test.Text = "{" + s.Split(' ')[0] + "}";
                        }
                    });}

    private void Refresh()
    {
        _expressions.ItemsSource = ExpressionEngine.Examples
            .Select(e => $"{e.Key}  —  {e.Description}")
            .ToList();
    }
}

/// <summary>Profile group editor (Cybersole.Ui.Views.Profiles.Modals.ProfileGroupView).</summary>
public sealed class ProfileGroupView : UserControl
{
    /// <summary>Bound as <c>Delete</c>; the button with that label runs this command.</summary>
    public ICommand Delete { get; }

    /// <summary>Bound as <c>Save</c>; the button with that label runs this command.</summary>
    public ICommand Save { get; }



    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>
    public bool CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    /// <summary>The group name on screen (bound as <c>GroupName</c>). Updated as the box changes.</summary>
    public string GroupName => _typedName;

    private string _typedName = string.Empty;

    private readonly AppServices _services;
    private readonly ListBox _groups = new() { Height = 200 };
    private readonly TextBlock _status = UiKit.Status();

    /// <summary>Bound as <c>Close</c>; closes the hosting window (was a bool method).</summary>
    public ICommand Close { get; }

    public ProfileGroupView(AppServices services)
    {
        Close = new RelayCommand(() => CloseCore());

        _services = services;
        var name = UiKit.Text(watermark: "Group name");
        name.TextChanged += (_, _) => _typedName = name.Text ?? string.Empty;

        Content = new StackPanel
        {
            Spacing = 6,
            Children =
            {
                UiKit.Title("Profile groups"),
                _groups,
                UiKit.Row("Name", name),
                UiKit.Buttons(
                    UiKit.Button("Save", () => Save.Execute(null)),
                    UiKit.Button("Delete", () => Delete.Execute(null))),
                _status,
            },
        };

        Refresh();
    
        Delete = new RelayCommand(() => {
                        if (_groups.SelectedIndex < 0) return;
                        _services.Config.BillingGroups.RemoveAt(_groups.SelectedIndex);
                        if (_services.Config.BillingGroups.Count == 0)
                            _services.Config.BillingGroups.Add(new BillingGroup { Name = "Group 1" });
                        _services.Config.Save();
                        Refresh();
                        _status.Text = "Group deleted.";
                    });
        Save = new RelayCommand(() => {
                        if (string.IsNullOrWhiteSpace(name.Text)) return;
                        _services.Config.BillingGroups.Add(new BillingGroup { Name = name.Text! });
                        _services.Config.Save();
                        Refresh();
                        _status.Text = "Group added.";
                    });}

    public void Refresh() => _groups.ItemsSource = _services.Config.BillingGroups
        .Select(g => $"{g.Name}  ({g.Profiles.Count} profiles)")
        .ToList();
}

/// <summary>
/// Profiles page (Cybersole.Ui.Views.Profiles.ProfileView) — the recovered commands are
/// Clear / Clone / CreateGroup / CreateTest / Delete / DeleteSelected / EditSelected /
/// Groups / MoveGroup / OpenCreator / OpenCsvEditor / OpenSettings.
/// </summary>
public sealed class ProfileView : UserControl
{
    /// <summary>Bound as <c>Delete</c>: the same command the "Delete selected" button carries.</summary>
    public ICommand Delete { get; }


    // ------------------------------------------------ copy from the image's locale (R395)

    /// <summary>"Clone Profiles" — the context menu's clone entry.</summary>
    public const string ContextClone = "Clone Profiles";

    /// <summary>"Create Test Profile" — the context menu's test entry.</summary>
    public const string ContextCreateTest = "Create Test Profile";

    /// <summary>"Open in CSV Editor" — the context menu's csv entry.</summary>
    public const string ContextCsvEditor = "Open in CSV Editor";

    /// <summary>"Delete Profiles" — the context menu's delete entry.</summary>
    public const string ContextDelete = "Delete Profiles";

    /// <summary>"Edit Profiles" — the context menu's edit entry.</summary>
    public const string ContextEdit = "Edit Profiles";

    /// <summary>"Delete {0} profiles?" — the delete confirmation's title.</summary>
    public const string DeleteConfirmTitleFormat = "Delete {0} profiles?";

    /// <summary>The delete confirmation's body.</summary>
    public const string DeleteConfirmMessageFormat =
        "Are you sure you want to delete {0} profiles?\nYou cannot undo this action.";

    /// <summary>"Delete ({0}) profiles" — the confirmation's action button.</summary>
    public const string DeleteConfirmActionFormat = "Delete ({0}) profiles";

    /// <summary>Shown when a search matches no profile.</summary>
    public const string NoResultsSubtitle = "There are no profiles matching your search";

    /// <summary>"{0} Profiles Loaded" / "1 Profile Loaded" — the page footer.</summary>
    public const string LoadedFormat = "{0} Profiles Loaded";

    /// <summary>The singular footer.</summary>
    public const string LoadedOne = "1 Profile Loaded";

    /// <summary>"{0} PROFILES SELECTED" / "{0} PROFILE SELECTED" — the selection counter.</summary>
    public const string SelectedManyFormat = "{0} PROFILES SELECTED";

    /// <summary>The singular selection counter.</summary>
    public const string SelectedOneFormat = "{0} PROFILE SELECTED";

    /// <summary>The footer for <paramref name="count"/> profiles.</summary>
    /// <summary>"No Profiles Loaded" — the zero form (Profiles.LoadedNone).</summary>
    public const string LoadedNone = "No Profiles Loaded";

    public static string Loaded(int count) => count switch
    {
        0 => LoadedNone,
        1 => LoadedOne,
        _ => string.Format(LoadedFormat, count),
    };

    /// <summary>The selection counter, singular when one profile is selected.</summary>
    public static string SelectionCaption(int count) =>
        string.Format(count == 1 ? SelectedOneFormat : SelectedManyFormat, count);

    private readonly AppServices _services;
    private readonly ListBox _profiles = new() { Height = 340 };
    private readonly ComboBox _groups = new() { Width = 220 };
    private readonly TextBlock _status = UiKit.Status();
    private bool _refreshing;

    // ------------------------------------------------ bound commands (R250)
    //
    // The original binds CreateGroup / CreateTest / MoveGroup / OpenCreator / OpenCsvEditor / OpenSettings on
    // ProfileView (analysis/xaml_bindings.json). Every one of them was already reachable as a button or inline lambda;
    // the names are what a keybind or a rebinding addresses.

    /// <summary>The billing-group names the combo lists (bound as <c>Groups</c>).</summary>
    public IReadOnlyList<string> Groups =>
        _services.Config.BillingGroups.Select(g => g.Name).ToList();

    /// <summary>
    /// Deletes the profile selected in the list and saves (bound as <c>DeleteSelected</c>). The list the page shows is the
    /// selected billing group's profiles, so that is where the removal happens.
    /// </summary>
    private bool DeleteSelectedCore()
    {
        var index = _profiles.SelectedIndex;
        var group = Selected();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        group.Profiles.RemoveAt(index);
        _services.Config.Save();
        Refresh();
        return true;
    }

    /// <summary>Opens the editor for the profile selected in the list (bound as <c>EditSelected</c>).</summary>
    private bool EditSelectedCore()
    {
        var index = _profiles.SelectedIndex;
        var group = Selected();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        OpenProfileEditor(group.Profiles[index].Id);
        return true;
    }


    /// <summary>Opens the group editor (bound as <c>CreateGroup</c>).</summary>
    private void CreateGroupCore() => ViewHostModal.Show(this, "Profile groups", new ProfileGroupView(_services));

    /// <summary>Opens the CSV editor (bound as <c>OpenCsvEditor</c>).</summary>
    private void OpenCsvEditorCore() =>
        ViewHostModal.Show(this, "CSV profile editor", new ProfileCsvEditorView(_services));

    /// <summary>Opens the profile creator for a new profile (bound as <c>OpenCreator</c>).</summary>
    private void OpenCreatorCore() => OpenProfileEditor(null);

    /// <summary>
    /// Opens Settings' browser-profile page — the profiles this app checks out with are Chrome profiles
    /// (bound as <c>OpenSettings</c>).
    /// </summary>
    private bool OpenSettingsCore()
    {
        if (TopLevel.GetTopLevel(this) is not MainWindow shell) return false;
        return shell.Navigate("Settings");
    }

    /// <summary>Runs the generator test against the current template (bound as <c>CreateTest</c>).</summary>
    public string CreateTest(string template)
    {
        var result = ExpressionEngine.Evaluate(template ?? string.Empty);
        _status.Text = result;
        return result;
    }

    /// <summary>
    /// Moves the profile at <paramref name="index"/> in the current list into another group (bound as <c>MoveGroup</c>).
    /// Returns the profile's new group id, or null when the move could not happen.
    /// </summary>
    public string? MoveGroup(int index, string targetGroupId)
    {
        if (string.IsNullOrWhiteSpace(targetGroupId)) return null;

        var target = _services.Config.BillingGroups.FirstOrDefault(g => g.Id == targetGroupId);
        if (target is null) return null;

        var current = CurrentGroup();
        if (current is null || index < 0 || index >= current.Profiles.Count) return null;

        var profile = current.Profiles[index];
        current.Profiles.RemoveAt(index);
        target.Profiles.Add(profile);
        _services.Config.Save();
        Refresh();
        _status.Text = $"Moved {profile.Name} to {target.Name}.";
        return target.Id;
    }

    /// <summary>The group the picker has selected.</summary>
    private BillingGroup? CurrentGroup()
    {
        var index = _groups.SelectedIndex;
        var groups = _services.Config.BillingGroups;
        return index >= 0 && index < groups.Count ? groups[index] : groups.FirstOrDefault();
    }

    /// <summary>
    /// R476: the original binds <c>Clone</c> / <c>Clear</c> as **properties** on this view. Both already work
    /// (clone copies every field via <c>Profile.Clone</c>; clear empties the group) — they were lambdas wired
    /// straight to buttons, so only their exposure changes.
    /// </summary>
    public ICommand Clone { get; }

    /// <inheritdoc cref="Clone"/>
    public ICommand Clear { get; }

    // R494: bound names for actions that already existed as methods (descriptor table: Getter+Setter).
    /// <summary>Bound as <c>CreateGroup</c>; behaviour unchanged (was a method).</summary>
    public ICommand CreateGroup { get; }

    /// <summary>Bound as <c>OpenCsvEditor</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenCsvEditor { get; }

    /// <summary>Bound as <c>OpenCreator</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenCreator { get; }

    /// <summary>Bound as <c>DeleteSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand DeleteSelected { get; }

    /// <summary>Bound as <c>EditSelected</c>; behaviour unchanged (was a method).</summary>
    public ICommand EditSelected { get; }

    /// <summary>Bound as <c>OpenSettings</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenSettings { get; }

    public ProfileView(AppServices services)
    {
        CreateGroup = new RelayCommand(CreateGroupCore);
        OpenCsvEditor = new RelayCommand(OpenCsvEditorCore);
        OpenCreator = new RelayCommand(OpenCreatorCore);
        DeleteSelected = new RelayCommand(() => DeleteSelectedCore());
        EditSelected = new RelayCommand(() => EditSelectedCore());
        OpenSettings = new RelayCommand(() => OpenSettingsCore());
        _services = services;
        Clone = new RelayCommand(CloneSelected);
        Clear = new RelayCommand(ClearProfiles);
        _groups.SelectionChanged += (_, _) => Refresh();

                var deleteButton = UiKit.Button("Delete selected", () =>
                    {
                        var group = Selected();
                        if (group is null || _profiles.SelectedIndex < 0) return;
                        group.Profiles.RemoveAt(_profiles.SelectedIndex);
                        _services.Config.Save();
                        Refresh();
                        _status.Text = "Profile deleted.";                    });
        Delete = deleteButton.Command!;

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
                        new TextBlock { Text = "Group", VerticalAlignment = VerticalAlignment.Center },
                        _groups,
                    },
                },
                _profiles,
                UiKit.Buttons(
                    UiKit.Button("Open creator", () => OpenProfileEditor(null)),
                    // Round 181: these two said "No CSV editor window exists yet" and "No group
                    // editor window exists yet". Both views are in this file —
                    // ProfileCsvEditorView at line 260, ProfileGroupView at line 474 — and both
                    // were complete UserControls. The missing thing was the window, not the view;
                    // ViewHostModal supplies it.
                    UiKit.Button("Open CSV editor", () => ViewHostModal.Show(this,
                        "CSV profile editor", new ProfileCsvEditorView(_services))),
                    UiKit.Button("Create group", () => ViewHostModal.Show(this,
                        "Profile groups", new ProfileGroupView(_services))),
                    UiKit.Button("Create test", () => CreateTestProfile()),
                    UiKit.Button("Clone", () => Clone.Execute(null)),
                    // R64: Profiles.Context.MoveTo ("Move profiles to"). Was the only MoveTo in
                    // the locale with no implementation for profiles.
                    UiKit.Button("Move to", () =>
                    {
                        var group = Selected();
                        if (group is null || _profiles.SelectedIndex < 0) return;

                        ProfileMoveView.Show(this, group.Profiles[_profiles.SelectedIndex],
                            _services.Config.BillingGroups, group, () =>
                            {
                                _services.Config.Save();
                                Refresh();
                                _status.Text = "Profile moved.";
                            });
                    }),
                    deleteButton,
                    UiKit.Button("Clear", () => Clear.Execute(null)),
                    UiKit.Button("Open settings", () => Status("Switch to the Settings tab above to change these."))),
                _status,
            },
        };

        Refresh();
    }

    private void Status(string text) => _status.Text = text;

    /// <summary>Duplicates the selected profile (lifted out of the old button lambda, R476).</summary>
    private void CloneSelected()
    {
        var group = Selected();
        if (group is null || _profiles.SelectedIndex < 0) return;

        // R63: was a hand-listed thirteen fields, dropping the four card fields and
        // eleven others - a clone that could not check out. Profile.Clone copies
        // every field with a new Id.
        group.Profiles.Add(group.Profiles[_profiles.SelectedIndex].Clone());
        _services.Config.Save();
        Refresh();
        _status.Text = "Profile cloned.";
    }

    /// <summary>Empties the selected group (lifted out of the old button lambda, R476).</summary>
    private void ClearProfiles()
    {
        var group = Selected();
        if (group is null) return;
        group.Profiles.Clear();
        _services.Config.Save();
        Refresh();
        _status.Text = "Profiles cleared.";
    }

    private BillingGroup? Selected()
    {
        var index = _groups.SelectedIndex;        if (index < 0 || index >= _services.Config.BillingGroups.Count) return null;
        return _services.Config.BillingGroups[index];
    }

    /// <summary>
    /// Open the profile editor for a new profile.
    ///
    /// "Open creator" used to only write "Profile creator opened." to the status line, and
    /// ProfileEditorWindow — which does exist — had no caller from this page at all. Same defect
    /// as the five buttons in TasksViews (rounds 97 and 99).
    /// </summary>
    private void OpenProfileEditor(string? existingId)
    {
        var owner = TopLevel.GetTopLevel(this) as Window;
        if (owner is null)
        {
            Status("No owner window — cannot open the editor.");
            return;
        }

        var editor = new ProfileEditorWindow(_services);
        editor.Closed += (_, _) => { _services.Config.Save(); Refresh(); };
        _ = editor.ShowDialog(owner);
        Status(existingId is null ? "Profile creator opened." : $"Editing {existingId}.");
    }

    /// <summary>
    /// Add a throwaway profile to the selected group so the profile list, the clone path and the
    /// editor all have something to work on without hand-editing config.json.
    /// </summary>
    private void CreateTestProfile()
    {
        var group = Selected();
        if (group is null)
        {
            Status("Select a profile group first.");
            return;
        }

        group.Profiles.Add(new Profile
        {
            Name = $"test-{group.Profiles.Count + 1}",
            Email = string.Empty,
        });

        _services.Config.Save();
        Refresh();
        Status($"Added a test profile to {group.Name}.");
    }

    public void Refresh()
    {
        if (_refreshing) return;
        _refreshing = true;
        try
        {
            var names = _services.Config.BillingGroups.Select(g => g.Name).ToList();
            var current = _groups.ItemsSource as IList<string>;
            if (current is null || !names.SequenceEqual(current))
                _groups.ItemsSource = names;
            if (_groups.SelectedIndex < 0) _groups.SelectedIndex = 0;

            var group = Selected();
            _profiles.ItemsSource = group is null
                ? new List<string>()
                : group.Profiles.Select(p => p.Display + "  " + p.Email + "  " + p.Last4).ToList();
        }
        finally
        {
            _refreshing = false;
        }
    }
}
