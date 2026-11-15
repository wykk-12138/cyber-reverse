using Newtonsoft.Json;

namespace Cybersole.Core.Models;

/// <summary>
/// One executed step of a web task (Cybersole.Models.TaskStep).
/// The original app renders these live under the task row; each store module
/// pushes a named step before performing work so a failure points at the frame
/// that broke instead of "checkout failed".
/// </summary>
public sealed class TaskStep : ObservableObject
{
    private string _name = string.Empty;
    private bool _completed;
    private bool _running;
    private DateTimeOffset? _started;
    private TimeSpan? _duration;
    private string? _error;

    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public bool Completed { get => _completed; set => SetProperty(ref _completed, value); }
    public bool Running { get => _running; set => SetProperty(ref _running, value); }
    public DateTimeOffset? Started { get => _started; set => SetProperty(ref _started, value); }
    public TimeSpan? Duration { get => _duration; set => SetProperty(ref _duration, value); }
    public string? Error { get => _error; set => SetProperty(ref _error, value); }

    public TaskStep Begin()
    {
        Started = DateTimeOffset.UtcNow;
        Running = true;
        Completed = false;
        return this;
    }

    public TaskStep End(bool ok, string? error = null)
    {
        Running = false;
        Completed = ok;
        Error = error;
        if (Started is { } s) Duration = DateTimeOffset.UtcNow - s;
        return this;
    }

    public override string ToString() =>
        $"{Name}{(Completed ? " ok" : "")}{(Error is null ? "" : " -> " + Error)}";
}

/// <summary>A single monitor observation (Cybersole.Models.MonitorEvent).</summary>
public sealed class MonitorEvent
{
    public string Name { get; set; } = string.Empty;
    public string? Store { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? Type { get; set; }
    public string? Message { get; set; }
}

/// <summary>What a monitor poll saw, kept for the monitor feed (Cybersole.Models.MonitorProduct).</summary>
public sealed class MonitorProduct
{
    public string? Image { get; set; }
    public string? Price { get; set; }
    public Input? Input { get; set; }
    public List<string> AvailableVariants { get; set; } = new();
}

/// <summary>
/// The monitor feed's input binding target (Cybersole.Models.Input).
///
/// <para>
/// R434: added because the binding table declares this type and the replica had no such class at all.
/// Evidence — the compiled XAML descriptor string at <c>0x14321141a</c> carries
/// <c>Cybersole.Models.Input,Cybersole.Core.Type!Getter</c> immediately after the MonitorProduct /
/// MonitorEvent members, i.e. the feed reaches <c>Type</c> through <c>MonitorProduct.Input</c>.
/// </para>
/// <para>
/// Why the gap went unseen: <c>bind_diff.py</c> only asks "does the member name appear anywhere in src/"
/// and <c>bind_scope.py</c> only asks "is the member inside that type's body" — neither can report a type
/// that does not exist, and <c>Type</c> is a very common member name elsewhere. R434 added
/// <c>bind_diff.py --type-presence</c> to measure this third class of gap.
/// </para>
/// </summary>
public sealed class Input : ObservableObject
{
    private string? _type;

    public string? Type
    {
        get => _type;
        set => SetProperty(ref _type, value);
    }
}

/// <summary>A shipping / billing address block (Cybersole.Models.Address).</summary>
public sealed class Address : ObservableObject
{
    private string? _firstName;
    private string? _lastName;
    private string? _address1;
    private string? _address2;
    private string? _city;
    private string? _state;
    private string? _zipCode;
    private string? _country;
    private string? _barangay;

    public string? FirstName { get => _firstName; set => SetProperty(ref _firstName, value); }
    public string? LastName { get => _lastName; set => SetProperty(ref _lastName, value); }
    public string? Address1 { get => _address1; set => SetProperty(ref _address1, value); }
    public string? Address2 { get => _address2; set => SetProperty(ref _address2, value); }
    public string? City { get => _city; set => SetProperty(ref _city, value); }
    public string? State { get => _state; set => SetProperty(ref _state, value); }
    public string? ZipCode { get => _zipCode; set => SetProperty(ref _zipCode, value); }
    public string? Country { get => _country; set => SetProperty(ref _country, value); }
    /// <summary>Philippine sub-municipality field; the original exposes it verbatim.</summary>
    public string? Barangay { get => _barangay; set => SetProperty(ref _barangay, value); }

    [JsonIgnore]
    public string FullName =>
        string.Join(' ', new[] { FirstName, LastName }.Where(s => !string.IsNullOrWhiteSpace(s)));
}

/// <summary>A payment card (Cybersole.Models.Card).</summary>
public sealed class Card : ObservableObject
{
    private string? _number;
    private string? _cvv;
    private string? _month;
    private string? _year;
    private string? _name;

    public string? Number { get => _number; set => SetProperty(ref _number, value); }
    public string? Cvv { get => _cvv; set => SetProperty(ref _cvv, value); }
    public string? Month { get => _month; set => SetProperty(ref _month, value); }
    public string? Year { get => _year; set => SetProperty(ref _year, value); }
    public string? Name { get => _name; set => SetProperty(ref _name, value); }

    [JsonIgnore] public string Last4 => Number is { Length: >= 4 } n ? n[^4..] : string.Empty;
}

/// <summary>Country option with its state list (Cybersole.Models.Country).</summary>
public sealed class Country
{
    public string Code { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public List<string> States { get; set; } = new();
}

/// <summary>Generic on/off named flag (Cybersole.Models.Flag).</summary>
public sealed class Flag : ObservableObject
{
    private string _name = string.Empty;
    private bool _enabled;
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public bool Enabled { get => _enabled; set => SetProperty(ref _enabled, value); }
}

/// <summary>A store element mapping (Cybersole.Elements.Element).</summary>
public sealed class Element
{
    public string Name { get; set; } = string.Empty;
    public string? PropName { get; set; }
    public string? Value { get; set; }
}

/// <summary>Keyboard shortcut binding row (Cybersole.Models.Shortcut).</summary>
public sealed class Shortcut : ObservableObject
{
    private string _name = string.Empty;
    private KeyBind? _gesture;
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public KeyBind? Gesture { get => _gesture; set => SetProperty(ref _gesture, value); }
}
