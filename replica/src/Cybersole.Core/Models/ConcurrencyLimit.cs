namespace Cybersole.Core.Models;

/// <summary>
/// How a <see cref="ConcurrencyMode"/> turns the settings into a number of monitoring tasks.
///
/// <para>
/// R930. The three modes come from the locale, and one of them states its own rule: <c>Both</c> means "the amount of
/// monitoring tasks will be equal to whichever is greater" of the maximum and the ratio. That sentence is the only
/// specification of the arithmetic anywhere in the recovered material, so it is implemented here rather than in a
/// caller, and the other two follow from their names.
/// </para>
///
/// <para>
/// <b>Why a separate function.</b> Three consumers need this figure — the task engine's gate, the settings preview and
/// any test — and a rule this small is exactly the kind that gets re-derived slightly differently in each. One
/// implementation makes them agree by construction.
/// </para>
///
/// <para>
/// <b>What is inference.</b> Rounding. A ratio of a whole number of tasks need not be whole, and nothing recovered says
/// which way it goes. Rounding down is chosen and labelled: over-starting a monitor pool is the failure that matters,
/// because the mode exists to limit concurrency rather than to reach a target.
/// </para>
/// </summary>
public static class ConcurrencyLimit
{
    /// <summary>
    /// The number of tasks a mode allows, given how many tasks exist, a maximum and a ratio in 0..1.
    ///
    /// <para>
    /// A maximum of zero or less means the maximum is not a limit: the mode then falls back to the task count, so a
    /// settings file with nothing set behaves as "no cap" rather than as "zero tasks", which would start nothing.
    /// </para>
    /// </summary>
    public static int Resolve(ConcurrencyMode mode, int taskCount, int maximum, double ratio)
    {
        if (taskCount <= 0) return 0;

        var byRatio = (int)Math.Floor(taskCount * Math.Clamp(ratio, 0d, 1d));
        var hasMaximum = maximum > 0;

        return mode switch
        {
            ConcurrencyMode.Maximum => hasMaximum ? Math.Min(maximum, taskCount) : taskCount,
            ConcurrencyMode.Ratio => byRatio,
            // the locale's own words: whichever is greater
            ConcurrencyMode.Both => Math.Min(taskCount, Math.Max(hasMaximum ? maximum : 0, byRatio)),
            _ => taskCount,
        };
    }

    /// <summary>The same figure for a settings object, so a caller does not have to unpack it.</summary>
    public static int Resolve(ConcurrencyMode mode, int taskCount, ConcurrencySettings settings) =>
        Resolve(mode, taskCount, settings?.Maximum ?? 0, settings?.Ratio ?? 0d);
}