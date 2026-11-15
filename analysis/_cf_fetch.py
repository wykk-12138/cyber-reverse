import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()

# 1) keep services so the bound member can reach the configuration
t = t.replace('''    public static readonly IReadOnlyList<string> Providers = new[] { "uncaptcha.io" };

    public CloudflareSolversView(AppServices services)
    {
        var s = services.Config.Settings;''',
'''    public static readonly IReadOnlyList<string> Providers = new[] { "uncaptcha.io" };

    private readonly AppServices _solverServices;

    /// <summary>
    /// Asks the configured Cloudflare solver for its balance and stores it (bound as <c>FetchBalance</c>). Returns the line
    /// the page prints, so the button and any keybind report the same thing.
    /// </summary>
    public string FetchBalance()
    {
        var settings = _solverServices.Config.Settings;
        var cf = settings.CloudflareSolvers.FirstOrDefault();
        if (cf is null) return "No Cloudflare provider configured.";
        if (cf.ApiKey is not { Length: > 0 })
            return $"{cf.Name}: no API key, so no balance to ask for.";

        var driver = _solverServices.Captcha.Registry.Driver("uncaptcha");
        cf.Balance = driver?.GetBalanceAsync(_solverServices.Http, new CaptchaProviderConfig
        {
            Type = "uncaptcha",
            Name = cf.Name,
            ApiKey = cf.ApiKey,
        }, default).GetAwaiter().GetResult() is { } balance ? (double)balance : 0;

        _solverServices.Config.Save();
        return $"{cf.Name}: {cf.Balance}";
    }

    public CloudflareSolversView(AppServices services)
    {
        _solverServices = services;
        var s = services.Config.Settings;''', 1)

# 2) the button goes through the member
old_lambda = t[t.index('                        UiKit.Button("Fetch balance", () =>'):t.index('                        }))),', t.index('                        UiKit.Button("Fetch balance", () =>')) + len('                        }))),')]
new_lambda = '''                        UiKit.Button("Fetch balance", () =>
                        {
                            status.Text = FetchBalance();
                            Refresh();
                        }))),'''
t = t.replace(old_lambda, new_lambda, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('FetchBalance extracted')
