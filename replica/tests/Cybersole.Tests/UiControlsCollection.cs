using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Tests that construct real Avalonia controls run one at a time.
///
/// <para>
/// R59: <c>ProxyRowTestTests.TheRowMenuTestsThatRow</c> and
/// <c>ProxyClearTests.ClearOverDoesNothingWithoutALimit</c> both passed when run alone and both
/// failed in the full suite. The cause is not the assertions — it is that xunit runs test classes
/// in parallel by default, and two threads building control trees touch Avalonia's static state.
/// </para>
///
/// <para>
/// This collection serialises exactly those classes. The alternative — a headless Avalonia
/// fixture with a dispatcher — would let them run in parallel, but it also creates an
/// <c>Application</c>, which changes what the controls do. These tests assert structure (which
/// menu items exist, what a handler was called with), not rendering, so they do not need one.
/// </para>
///
/// <para>
/// Only put a class here if it builds controls. Everything else should stay parallel.
/// </para>
/// </summary>
[CollectionDefinition(Name, DisableParallelization = true)]
public sealed class UiControlsCollection
{
    public const string Name = "ui-controls";
}
