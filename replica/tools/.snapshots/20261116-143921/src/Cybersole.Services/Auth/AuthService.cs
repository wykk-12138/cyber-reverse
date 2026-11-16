using System.Net.Http.Headers;
using System.Text;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;

namespace Cybersole.Services.Auth;

/// <summary>Decoded JWT payload (subset of the claims used by Cybersole).</summary>
public sealed class JwtClaims
{
    public string? Subject { get; init; }
    public string? Email { get; init; }
    public string? Role { get; init; }
    public string? SecurityStamp { get; init; }
    public DateTimeOffset? Expires { get; init; }
    public string? Issuer { get; init; }
    public string? Audience { get; init; }

    public bool IsExpired => Expires is { } e && e <= DateTimeOffset.UtcNow;
}

public static class Jwt
{
    /// <summary>Decode a JWT payload without validating the signature.</summary>
    public static JwtClaims? Decode(string? token)
    {
        if (string.IsNullOrWhiteSpace(token)) return null;
        var parts = token.Split('.');
        if (parts.Length < 2) return null;
        try
        {
            var json = Encoding.UTF8.GetString(Base64UrlDecode(parts[1]));
            var obj = Newtonsoft.Json.Linq.JObject.Parse(json);
            return new JwtClaims
            {
                Subject = (string?)obj["sub"] ?? (string?)obj["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"],
                Email = (string?)obj["name"] ?? (string?)obj["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"],
                Role = (string?)obj["http://schemas.microsoft.com/ws/2008/06/identity/claims/role"],
                SecurityStamp = (string?)obj["AspNet.Identity.SecurityStamp"],
                Expires = obj["exp"]?.ToObject<long>() is { } exp ? DateTimeOffset.FromUnixTimeSeconds(exp) : null,
                Issuer = (string?)obj["iss"],
                Audience = (string?)obj["aud"],
            };
        }
        catch
        {
            return null;
        }
    }

    private static byte[] Base64UrlDecode(string s)
    {
        s = s.Replace('-', '+').Replace('_', '/');
        switch (s.Length % 4)
        {
            case 2: s += "=="; break;
            case 3: s += "="; break;
        }
        return Convert.FromBase64String(s);
    }
}

/// <summary>
/// Authentication service (Cybersole.Services.Auth).
/// Owns the bearer token, the OAuth hand-off and session validation.
/// </summary>
public sealed class AuthService
{
    public const string ApiBase = "https://api.cybersole.io";
    public const string WebBase = "https://cybersole.io";

    private readonly NetClient _http;
    private readonly EventBus _bus;
    private readonly GlobalSettings _settings;

    public AuthService(NetClient http, EventBus bus, GlobalSettings settings)
    {
        _http = http;
        _bus = bus;
        _settings = settings;
        if (!string.IsNullOrWhiteSpace(settings.Bearer))
            Claims = Jwt.Decode(settings.Bearer);
    }

    public string? Bearer { get; private set; }
    public JwtClaims? Claims { get; private set; }
    public bool IsSignedIn => Bearer is not null && Claims is { IsExpired: false };
    public string? Email => Claims?.Email;

    public event EventHandler? SignedIn;
    public event EventHandler? SignedOut;

    /// <summary>Opens the OAuth authorization URL that the desktop client hands to the browser.</summary>
    public string BuildOAuthUrl(string redirectUri = "cybersole://auth")
        => $"{WebBase}/oauth/authorize?client_id=cybersole-desktop&redirect_uri={Uri.EscapeDataString(redirectUri)}&response_type=code";

    /// <summary>Exchanges an authorization code for a bearer token.</summary>
    public async Task<bool> ExchangeCodeAsync(string code, CancellationToken ct = default)
    {
        var res = await _http.PostJsonAsync($"{ApiBase}/auth/token",
            $"{{\"code\":\"{code.Replace("\"", string.Empty)}\",\"grant_type\":\"authorization_code\"}}",
            new RequestOptions { Tag = "auth" }, ct).ConfigureAwait(false);

        if (!res.IsSuccess)
        {
            _bus.Warn("Auth", $"token exchange failed: HTTP {res.StatusCode}");
            return false;
        }

        var token = Newtonsoft.Json.Linq.JObject.Parse(res.Body)["access_token"]?.ToString();
        if (string.IsNullOrEmpty(token)) return false;

        SetBearer(token);
        return true;
    }

    /// <summary>Email + password sign-in (fallback path used by LoginControl).</summary>
    public async Task<bool> SignInAsync(string email, string password, CancellationToken ct = default)
    {
        var res = await _http.PostJsonAsync($"{ApiBase}/auth/login",
            Newtonsoft.Json.JsonConvert.SerializeObject(new { email, password }),
            new RequestOptions { Tag = "auth" }, ct).ConfigureAwait(false);

        if (!res.IsSuccess)
        {
            _bus.Warn("Auth", $"sign-in failed: HTTP {res.StatusCode}");
            return false;
        }

        var token = Newtonsoft.Json.Linq.JObject.Parse(res.Body)["access_token"]?.ToString();
        if (string.IsNullOrEmpty(token)) return false;

        SetBearer(token);
        return true;
    }

    public void SetBearer(string token)
    {
        Bearer = token;
        Claims = Jwt.Decode(token);
        _settings.Bearer = token;
        _bus.Info("Auth", $"signed in as {Claims?.Email ?? "unknown"} (role={Claims?.Role})");
        SignedIn?.Invoke(this, EventArgs.Empty);
    }

    public void SignOut()
    {
        Bearer = null;
        Claims = null;
        _settings.Bearer = null;
        _bus.Info("Auth", "signed out");
        SignedOut?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Validates the current token against the API.</summary>
    public async Task<bool> ValidateAsync(CancellationToken ct = default)
    {
        if (Bearer is null) return false;
        var opts = Authorized("auth");
        var res = await _http.GetAsync($"{ApiBase}/me", opts, ct).ConfigureAwait(false);
        if (!res.IsSuccess)
        {
            _bus.Warn("Auth", $"session invalid (HTTP {res.StatusCode})");
            return false;
        }

        var body = Newtonsoft.Json.Linq.JObject.Parse(res.Body);
        _bus.Info("Auth", $"session ok: {body["email"]} plan={body["plan"]}");
        return true;
    }

    public RequestOptions Authorized(string? tag = null)
    {
        var opts = new RequestOptions { Tag = tag };
        if (Bearer is not null)
            opts.Headers["Authorization"] = $"Bearer {Bearer}";
        return opts;
    }
}
