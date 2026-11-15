using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Cybersole.Services;

/// <summary>
/// Finds the Chromium browser profiles on this machine.
///
/// The Payment settings page has a "Refresh" button next to "Checkout Profiles" that only echoed
/// the list already in settings — it never looked at the disk. A user who adds a Chrome profile
/// in the browser expects that button to notice; it did not.
///
/// What counts as a profile: a directory directly under <c>User Data</c> that either is named
/// <c>Default</c> or starts with <c>Profile </c>, and holds a <c>Preferences</c> file. That is the
/// same rule Chrome and Edge use, so "Guest Profile", "System Profile" and "Crashpad" are skipped
/// without hard-coding their names.
/// </summary>
public static class BrowserProfileScanner
{
    private static readonly (string Label, string[] Paths)[] Candidates =
    {
        ("Chrome", new[]
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Google", "Chrome", "User Data"),
        }),
        ("Chrome Beta", new[]
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Google", "Chrome Beta", "User Data"),
        }),
        ("Edge", new[]
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Microsoft", "Edge", "User Data"),
        }),
        ("Brave", new[]
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "BraveSoftware", "Brave-Browser", "User Data"),
        }),
    };

    /// <summary>
    /// Profile names as <c>"Chrome: Default"</c> style labels, sorted so the list is stable
    /// between calls. Returns an empty list when no Chromium browser is installed.
    /// </summary>
    public static List<string> Scan()
    {
        var found = new List<string>();

        foreach (var (label, roots) in Candidates)
        {
            foreach (var root in roots)
            {
                if (!Directory.Exists(root)) continue;

                IEnumerable<string> dirs;
                try { dirs = Directory.EnumerateDirectories(root); }
                catch { continue; }

                foreach (var dir in dirs)
                {
                    var name = Path.GetFileName(dir);
                    var looksLikeProfile = name.Equals("Default", StringComparison.OrdinalIgnoreCase)
                                           || name.StartsWith("Profile ", StringComparison.OrdinalIgnoreCase);
                    if (!looksLikeProfile) continue;

                    // a real profile has preferences; an empty leftover directory does not
                    if (!File.Exists(Path.Combine(dir, "Preferences"))) continue;

                    found.Add($"{label}: {name}");
                }
            }
        }

        return found.Distinct().OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToList();
    }
}
