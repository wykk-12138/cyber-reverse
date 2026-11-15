using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Serialises the tests that spawn an external Python process.
/// </summary>
/// <remarks>
/// R585 recorded a suite run of 1613 passed / **1 failed** that two re-runs could not reproduce (1631 and 1614
/// passed). The failing test's name was lost because the output went through a filter, so the cause is Unknown — but
/// one plausible mechanism is worth removing rather than shrugging at:
///
/// <c>ShapeAuditGuardTests</c>, <c>BindDiffGuardTests</c> and <c>BindScopeGuardTests</c> each start a `python`
/// child process, and xunit runs test <b>classes</b> in parallel by default. Three concurrent process launches plus
/// a loaded machine is exactly the shape of an intermittent failure.
///
/// Putting them in one collection makes them run one after another. That does not prove the failure is gone — a
/// flake that has not recurred cannot be shown fixed — but it removes a cause I can name. If the failure comes back
/// with a name attached, this note is the place to record what it turned out to be.
/// </remarks>
[CollectionDefinition("external-tools")]
public sealed class ExternalToolCollection
{
    // no fixtures: the collection exists only to serialise its members
}
