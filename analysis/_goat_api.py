import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs"
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Lift the CSRF token the page left in a cookie or a meta tag.</summary>'''
add = '''    // ── account surface (R328) ────────────────────────────────────────────────
    //
    // The image carries four /web-api/v1 paths this flow never used:
    //   POST /web-api/v1/login                    (path evidenced; body field names inferred)
    //   POST /web-api/v1/users/send_otp_token     (path evidenced; body field names inferred)
    //   GET  /web-api/v1/addresses                (path evidenced, no body)
    //   GET  /web-api/v1/billing_infos            (path evidenced, no body)
    // Evidence: https://www.goat.com/web-api/... literals in the 5.18.32 image. The paths are the image's; the request
    // bodies are not, so every body below is marked inferred.

    /// <summary>Signs in and keeps the session cookie (path evidenced; body inferred).</summary>
    private Task<NetResponse?> LoginAsync(FlowContext c, string email, string password, CancellationToken ct) =>
        PostJsonAsync(c, WebApi(c, "/v1/login"),
            "{\\"email\\":\\"" + JsonEscape(email) + "\\",\\"password\\":\\"" + JsonEscape(password) + "\\"}",
            "goat-login", ct);

    /// <summary>Asks for an OTP for this address (path evidenced; body inferred).</summary>
    private Task<NetResponse?> SendOtpAsync(FlowContext c, string email, CancellationToken ct) =>
        PostJsonAsync(c, WebApi(c, "/v1/users/send_otp_token"),
            "{\\"email\\":\\"" + JsonEscape(email) + "\\"}", "goat-otp", ct);

    /// <summary>The saved addresses (path evidenced, no body).</summary>
    private Task<NetResponse?> GetAddressesAsync(FlowContext c, CancellationToken ct) =>
        GetAsync(c, WebApi(c, "/v1/addresses"), "goat-addresses", ct);

    /// <summary>The saved billing records (path evidenced, no body).</summary>
    private Task<NetResponse?> GetBillingInfosAsync(FlowContext c, CancellationToken ct) =>
        GetAsync(c, WebApi(c, "/v1/billing_infos"), "goat-billing", ct);

    /// <summary>
    /// Makes sure the session knows which saved address to buy with. GOAT's purchase is keyed to one, so this fills
    /// <c>goat.addressId</c> from the first saved address when the task did not set it.
    /// </summary>
    private async Task<bool> EnsureAddressAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("goat.addressId", out var existing) && existing is { Length: > 0 })
            return true;

        var res = await GetAddressesAsync(c, ct).ConfigureAwait(false);
        if (res is not { IsSuccess: true }) return false;

        var id = FirstId(res.Body);
        if (string.IsNullOrEmpty(id)) return false;

        c.Session.Vars["goat.addressId"] = id;
        return true;
    }

    /// <summary>Pulls the first "id" value out of a JSON body; empty when there is none.</summary>
    private static string FirstId(string body)
    {
        var m = Regex.Match(body, "\\"id\\"\\\\s*:\\\\s*\\"?([A-Za-z0-9_\\\\-]+)", RegexOptions.IgnoreCase);
        return m.Success ? m.Groups[1].Value : string.Empty;
    }

    private static string JsonEscape(string value) =>
        value.Replace("\\\\", "\\\\\\\\", StringComparison.Ordinal).Replace("\\"", "\\\\\\"", StringComparison.Ordinal);

''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('four account methods + address helper added')
