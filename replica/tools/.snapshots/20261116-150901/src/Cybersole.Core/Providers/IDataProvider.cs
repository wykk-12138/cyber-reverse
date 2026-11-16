namespace Cybersole.Providers;

/// <summary>
/// <c>Cybersole.Providers.IDataProvider</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the member <c><c>Name</c></c> is bound by the original, with a getter.
/// <b>Inferred</b>: that this is an <c>interface</c> — the name's <c>I</c> prefix is the .NET convention and
/// <c>TYPE_GAPS.md</c> calls it a provider contract. The descriptor table records neither.
/// <b>Unknown</b>: behaviour, and every other member the contract may have.
/// </remarks>
public interface IDataProvider
{
    /// <summary>Bound as <c>Name</c> (getter only in the original) — getter only; text; type inferred.</summary>
    public string Name { get; }
}
