using System.Text.Json;
using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Cybersole.Stores.Scripts;

namespace Cybersole.Stores.Accounts;

/// <summary>
/// Google account linking, the way the live 5.18.32 build does it: instead of asking for an
/// email and a password in a form, the Add Account dialog opens an embedded Google sign-in
/// page, waits for the account to land on myaccount.google.com, and only then asks for the
/// display name and the proxy to bind.
///
/// This wraps <see cref="ChromiumBridge"/> — the same CDP bridge the
/// Nike Kasada path uses — so the sign-in is a real browser session rather than a scripted
/// form post. Google blocks scripted logins precisely because they skip the browser.
/// </summary>
public sealed class GoogleOAuthFlow : IAsyncDisposable
{
    public const string SignInUrl = "https://accounts.google.com/signin";

    /// <summary>Where the flow lands when the account is authenticated.</summary>
    public const string SignedInMarker = "myaccount.google.com";

    private readonly ChromiumBridge? _bridge;

    private GoogleOAuthFlow(ChromiumBridge? bridge) => _bridge = bridge;

    /// <summary>Launch a browser and open the Google sign-in page.</summary>
    public static async Task<GoogleOAuthFlow> BeginAsync(string? executable = null,
        CancellationToken ct = default)
    {
        var bridge = await ChromiumBridge
            .LaunchAsync(executable, ct: ct).ConfigureAwait(false);

        await bridge.ApplyStealthAsync(ct: ct).ConfigureAwait(false);
        await bridge.NavigateAsync(SignInUrl, ct).ConfigureAwait(false);

        return new GoogleOAuthFlow(bridge);
    }

    /// <summary>Current URL, used to tell whether sign-in finished.</summary>
    public async Task<string?> CurrentUrlAsync(CancellationToken ct = default)
    {
        if (_bridge is null) return null;

        var raw = await _bridge.EvaluateAsync("location.href", ct).ConfigureAwait(false);
        return Unquote(raw);
    }

    /// <summary>
    /// Poll until the page leaves accounts.google.com for myaccount.google.com, or the budget
    /// runs out. Sign-in is interactive (password, 2FA), so this waits on the human.
    /// </summary>
    public async Task<bool> WaitForSignInAsync(TimeSpan timeout, CancellationToken ct = default)
    {
        var deadline = DateTime.UtcNow + timeout;

        while (DateTime.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();

            var url = await CurrentUrlAsync(ct).ConfigureAwait(false);
            if (url is not null && url.Contains(SignedInMarker, StringComparison.OrdinalIgnoreCase))
                return true;

            await Task.Delay(1000, ct).ConfigureAwait(false);
        }

        return false;
    }

    /// <summary>
    /// Read the signed-in identity out of the page. Google puts the address in the account
    /// chip's data attribute; the display name sits next to it.
    /// </summary>
    public async Task<(string? Email, string? Name)> ReadIdentityAsync(CancellationToken ct = default)
    {
        if (_bridge is null) return (null, null);

        const string probe = """
            (() => {
              const chip = document.querySelector('[data-email]');
              if (chip) {
                return JSON.stringify({
                  email: chip.getAttribute('data-email'),
                  name: chip.getAttribute('data-name') || chip.textContent.trim()
                });
              }
              const m = document.body.innerText.match(/[\\w.+-]+@[\\w-]+\\.[\\w.]+/);
              return JSON.stringify({ email: m ? m[0] : null, name: null });
            })()
            """;

        var raw = await _bridge.EvaluateAsync(probe, ct).ConfigureAwait(false);
        var json = Unquote(raw);
        if (string.IsNullOrEmpty(json)) return (null, null);

        try
        {
            using var doc = JsonDocument.Parse(json);
            var email = doc.RootElement.TryGetProperty("email", out var e) ? e.GetString() : null;
            var name = doc.RootElement.TryGetProperty("name", out var n) ? n.GetString() : null;
            return (email, name);
        }
        catch (JsonException)
        {
            return (null, null);
        }
    }

    /// <summary>
    /// Run the whole link: wait for sign-in, read the identity, and produce the account the
    /// caller should persist (display name and proxy still get filled in by the UI).
    /// </summary>
    public async Task<GoogleLinkResult> CompleteAsync(TimeSpan timeout,
        CancellationToken ct = default)
    {
        if (!await WaitForSignInAsync(timeout, ct).ConfigureAwait(false))
            return GoogleLinkResult.TimedOut();

        var (email, name) = await ReadIdentityAsync(ct).ConfigureAwait(false);
        if (string.IsNullOrEmpty(email))
            return GoogleLinkResult.NoIdentity();

        return new GoogleLinkResult
        {
            Success = true,
            Account = new GoogleAccount
            {
                Email = email!,
                Name = name ?? email!.Split('@')[0],
                State = "Linked",
            },
        };
    }

    public async ValueTask DisposeAsync()
    {
        if (_bridge is not null) await _bridge.DisposeAsync().ConfigureAwait(false);
    }

    /// <summary>CDP evaluate returns a JSON string; unwrap the quotes when present.</summary>
    private static string? Unquote(string? raw)
    {
        if (string.IsNullOrEmpty(raw)) return raw;
        var trimmed = raw.Trim();
        if (trimmed.Length > 1 && trimmed[0] == '"' && trimmed[^1] == '"')
        {
            try { return JsonSerializer.Deserialize<string>(trimmed); }
            catch (JsonException) { return trimmed; }
        }
        return trimmed;
    }

    /// <summary>True when the URL looks like a completed Google sign-in.</summary>
    public static bool LooksSignedIn(string? url) =>
        url is not null && url.Contains(SignedInMarker, StringComparison.OrdinalIgnoreCase);

    /// <summary>Pull an address out of arbitrary text, for tests and for the JS fallback.</summary>
    public static string? ExtractEmail(string? text) =>
        string.IsNullOrEmpty(text) ? null : Regex.Match(text, @"[\w.+-]+@[\w-]+\.[\w.]+").Value is { Length: > 0 } m ? m : null;
}

/// <summary>Outcome of a Google account link attempt.</summary>
public sealed class GoogleLinkResult
{
    public bool Success { get; init; }
    public GoogleAccount? Account { get; init; }
    public string? Error { get; init; }

    public static GoogleLinkResult TimedOut() => new()
    {
        Success = false,
        Error = "sign-in did not complete before the timeout",
    };

    public static GoogleLinkResult NoIdentity() => new()
    {
        Success = false,
        Error = "signed in, but no email address was readable from the page",
    };
}

