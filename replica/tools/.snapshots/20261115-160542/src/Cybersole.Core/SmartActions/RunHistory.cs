using System;

namespace Cybersole.SmartActions;

/// <summary>
/// <c>Cybersole.SmartActions.RunHistory</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Exception</c>, <c>Result</c>, <c>Timestamp</c>, <c>Trigger</c></c> are bound by the original, each with a getter and a setter.
/// <b>Inferred</b>: their CLR types and any cross-reference — the descriptor table records names and accessor
/// kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class RunHistory
{
    /// <summary>Bound as <c>Exception</c> — text; type inferred.</summary>
    public string Exception { get; set; } = string.Empty;

    /// <summary>Bound as <c>Result</c> — text; type inferred.</summary>
    public string Result { get; set; } = string.Empty;

    /// <summary>Bound as <c>Timestamp</c> — a point in time; inferred; type inferred.</summary>
    public DateTime Timestamp { get; set; }

    /// <summary>Bound as <c>Trigger</c> — text; type inferred.</summary>
    public string Trigger { get; set; } = string.Empty;
}
