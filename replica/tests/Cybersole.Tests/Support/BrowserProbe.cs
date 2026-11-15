using System;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;

namespace Cybersole.Tests.Support;

/// <summary>
/// Waits for a page to stop changing before a test measures it (R206).
///
/// <para>
/// The bug this exists for: Chromium re-installs <c>window.chrome</c> <b>after</b> the global prune has removed it, and
/// when it does so depends on how loaded the machine is. Waiting for <c>document.readyState === 'complete'</c> is not
/// enough — measured one suite run in eight ending with <c>extra[chrome]</c>, i.e. the prune had run, the page reported
/// complete, and the object had come back by the time the count was taken.
/// </para>
///
/// <para>
/// So the probe waits for the own-name count to be <b>stable across three samples 60 ms apart</b> (bounded at ~2 s)
/// before it measures. That is a measurement fix, not a product fix: the product keeps deleting on a timer, and this
/// stops the test from sampling during the window where both are true.
/// </para>
/// </summary>
public static class BrowserProbe
{
    /// <summary>Samples <c>Object.getOwnPropertyNames(window).length</c> until it stops moving, then returns.</summary>
    public static async Task SettleAsync(ChromiumBridge bridge, int stableSamples = 3, int maxSamples = 33)
    {
        var last = -1;
        var steady = 0;

        for (var i = 0; i < maxSamples; i++)
        {
            int count;
            try
            {
                var raw = await bridge.EvaluateAsync("String(Object.getOwnPropertyNames(window).length)");
                if (!int.TryParse(raw, out count)) count = last;
            }
            catch (Exception) { count = last; }

            if (count == last && count >= 0) steady++;
            else steady = 0;

            last = count;
            if (steady >= stableSamples - 1) return;

            await Task.Delay(60).ConfigureAwait(false);
        }
    }

    /// <summary>
    /// Waits until the actual <b>name list</b> — not its length — is identical across three samples.
    ///
    /// <para>
    /// R304: <see cref="SettleAsync"/> watches the count, which is a proxy. On 2026-11-13 the suite failed
    /// <c>NoNameIsAdvertisedWithoutAProperty</c> twice with a stable count and a different set, i.e. Chromium had swapped
    /// one name for another inside the same length. Measuring what the assertion measures removes that gap without
    /// weakening a single assertion.
    /// </para>
    /// </summary>
    public static async Task SettleNamesAsync(ChromiumBridge bridge, int stableSamples = 3, int maxSamples = 60)
    {
        string? last = null;
        var steady = 0;

        for (var i = 0; i < maxSamples; i++)
        {
            string? names;
            try
            {
                names = await bridge.EvaluateAsync("Object.getOwnPropertyNames(window).sort().join(',')");
            }
            catch (Exception) { names = last; }

            if (names == last && names is not null) steady++;
            else steady = 0;

            last = names;
            if (steady >= stableSamples - 1) return;

            await Task.Delay(60).ConfigureAwait(false);
        }
    }

    /// <summary>Readies a freshly navigated page: readyState complete, then a settled name count.</summary>
    public static async Task ReadyAsync(ChromiumBridge bridge)
    {
        for (var i = 0; i < 100; i++)
        {
            try
            {
                if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            }
            catch (Exception) { /* the document may still be swapping */ }
            await Task.Delay(50).ConfigureAwait(false);
        }

        await SettleAsync(bridge).ConfigureAwait(false);
    }
}
