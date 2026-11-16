using Cybersole.Core.Models;
using Cybersole.Services.Auth;
using LicenseModel = Cybersole.Core.Models.License;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;

namespace Cybersole.Services.Licensing;

public sealed class InvalidLicenseException : Exception
{
    public InvalidLicenseException(string message) : base(message) { }
}

public sealed class NoLicenseException : Exception
{
    public NoLicenseException(string message = "no license found") : base(message) { }
}

/// <summary>
/// License verification (Cybersole.Services.License).
/// Mirrors the original symbol set: VerifyLicense / FindLicense / ReadLicense /
/// LicenseFile / CheckLicense / LicenseVerifier / apisecuretoken.
/// </summary>
public sealed class LicenseService
{
    public const string SecureTokenUrl = "https://cybersole.io/api/apisecuretoken";
    public const string LicenseFileName = "license.key";

    private readonly NetClient _http;
    private readonly EventBus _bus;
    private readonly GlobalSettings _settings;
    private readonly AuthService _auth;

    public LicenseService(NetClient http, EventBus bus, GlobalSettings settings, AuthService auth)
    {
        _http = http;
        _bus = bus;
        _settings = settings;
        _auth = auth;
    }

    public LicenseModel? Current { get; private set; }
    public bool HasLicense => !string.IsNullOrWhiteSpace(_settings.License);
    public event EventHandler<LicenseModel>? Verified;

    /// <summary>Probe paths used by FindLicense (mirrors Bogus.Premium.LicenseKey probe list).</summary>
    public static IEnumerable<string> ProbePaths()
    {
        yield return Path.Combine(AppPaths.DataRoot, LicenseFileName);
        yield return Path.Combine(AppPaths.DataRoot, "license.json");
        yield return Path.Combine(AppContext.BaseDirectory, LicenseFileName);
    }

    public string? FindLicense()
    {
        foreach (var path in ProbePaths())
            if (File.Exists(path)) return path;
        return null;
    }

    public LicenseModel? ReadLicense(string path)
    {
        try
        {
            var json = File.ReadAllText(path);
            var lic = Json.Deserialize<LicenseModel>(json);
            if (lic is not null && string.IsNullOrEmpty(lic.Key)) lic.Key = json.Trim();
            return lic;
        }
        catch (Exception ex)
        {
            _bus.Error("License", $"read failed: {ex.Message}");
            return null;
        }
    }

    /// <summary>Local pre-check: shape + presence. Server remains the authority.</summary>
    public bool CheckLicense(string? key)
    {
        if (string.IsNullOrWhiteSpace(key)) return false;
        var trimmed = key.Trim();
        return trimmed.Length is >= 16 and <= 64 && trimmed.All(Uri.IsHexDigit);
    }

    /// <summary>
    /// Verify the license against the server and exchange it for a secure token.
    /// Throws <see cref="InvalidLicenseException"/> when the server rejects it.
    /// </summary>
    public async Task<bool> VerifyLicenseAsync(string licenseKey, CancellationToken ct = default)
    {
        if (!CheckLicense(licenseKey))
            throw new InvalidLicenseException("license format rejected locally");

        // Round 120 probed both hosts this service knows about:
        //
        //   GET  cybersole.io/api/apisecuretoken  -> 200, a sealed token (12-byte nonce,
        //                                            64-byte body, 64-byte tag)
        //   POST cybersole.io/api/apisecuretoken  -> 405 with Allow: GET
        //   api.cybersole.io/*                    -> 404 for every path except /health -> 200
        //
        // Round 176 corrected two of those:
        //
        //   - the token is NOT static. Sampling every 15 s for two minutes: t+0s one value,
        //     t+31s a different one, t+95s a third. Those gaps are 31 s and 64 s — one period of
        //     ~60 s seen from a phase offset, not two periods of ~30 s.
        //
        //     R176 read 31 s and wrote "roughly every 30 seconds", which the 64 s gap already
        //     contradicted. R217 sampled again (every 15 s, 170 s) and got changes at 31 s,
        //     93 s, 154 s — gaps of 62 s and 61 s.
        //
        //     R120 saw it unchanged because its two calls were seconds apart, and recorded that
        //     as "identical on every request" — true of consecutive calls, false of the token.
        //
        //   - api.cybersole.io is not "404 for everything except /health": /api/user answers 401
        //     and /api/apisecuretoken answers 200 with the same token the apex domain returns.
        //     Four paths were probed in R120; two more exist.
        //
        // So the previous POST could never succeed — it was rejected by the router before the key
        // was even looked at. The live build reads the sealed token and verifies locally; without
        // its key material this build cannot reproduce that, and pretending otherwise is worse
        // than reporting it.
        var res = await _http.GetAsync(SecureTokenUrl, _auth.Authorized("license"), ct)
            .ConfigureAwait(false);

        if (!res.IsSuccess)
            throw new InvalidLicenseException(
                $"the licence endpoint answered HTTP {res.StatusCode}; it accepts GET only and "
                + "this build has no key material to open the sealed token it returns");

        throw new InvalidLicenseException(
            "the licence endpoint returned a sealed token that this build cannot open. "
            + "Accepting the key anyway would be a fake activation, so it was rejected. "
            + $"Local format check passed for ****{Tail(licenseKey)}.");
    }

    /// <summary>Offline validation from the persisted settings key (no network).</summary>
    public bool ValidateOffline()
    {
        if (!HasLicense) throw new NoLicenseException();
        return CheckLicense(_settings.License);
    }

    private static string Tail(string key) => key.Length >= 4 ? key[^4..] : key;
}
