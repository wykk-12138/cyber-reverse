using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Serialises the tests that read and mutate the shared on-disk settings.
///
/// <para>
/// R1165 verified the mechanism rather than guessing at it: <c>AppPaths.DataRoot</c> is a static
/// initialised once per process (overridable through <c>CYBERSOLE_DATA_ROOT</c>) and
/// <c>AppServices.Create</c> calls <c>config.Load()</c> against that one root, so every test in a run
/// shares a single <c>settings.json</c>. Each test gets its own <c>AppServices</c> instance, but a class
/// that mutates and then asserts on <c>Config.TaskGroups</c> is still reading through the same file as
/// any other class doing the same at that moment, and xunit runs classes in parallel by default.
/// </para>
///
/// <para>
/// <c>GroupSummaryTests</c> has now failed twice in runs where it passes in isolation — once recorded in
/// R806 as <c>DeletingRemovesTheGroupOnce</c> and once in R1162 as
/// <c>CloningCopiesTheGroupAndItsTasks</c>, the second of which did not reproduce on a clean re-run.
/// Only that class is serialised here: the other eleven classes that touch <c>services.Config</c> are
/// candidates, not yet moved, and this collection exists so moving them is a one-line change each.
/// </para>
/// </summary>
[CollectionDefinition("shared-settings", DisableParallelization = true)]
public sealed class SharedSettingsCollection
{
}
