import io

# Solver: Name / Captcha / View / Reload — four bound names, all data-ish except Reload
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Checkout.cs"
t1 = io.open(p1, encoding='utf-8').read()
anchor = '''    public SolverSettings Settings { get; set; } = new();'''
add = '''    /// <summary>Row title in the solver list (bound as <c>Name</c>, R361).</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>The captcha this solver was asked about (bound as <c>Captcha</c>).</summary>
    public string? Captcha { get; set; }

    /// <summary>Whether the row is expanded in the list (bound as <c>View</c>).</summary>
    public bool View { get; set; }

    /// <summary>Bumped whenever the row is refreshed, so a view can tell "reload happened" (bound as <c>Reload</c>).</summary>
    public int Reload { get; private set; }

    /// <summary>Marks the row for a refresh (bound as <c>Reload</c>'s action).</summary>
    public void RequestReload() => Reload++;

''' + anchor
assert anchor in t1 and 'public string Name { get; set; } = string.Empty;\n\n    /// <summary>The captcha' not in t1
io.open(p1, 'w', encoding='utf-8', newline='').write(t1.replace(anchor, add, 1))
print('Solver gains Name/Captcha/View/Reload')

# CaptchaProvider: Count / BalanceSupported / IsFetchingBalance
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs"
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    public int Priority { get; set; }'''
add2 = '''    /// <summary>How many solves this provider has done (bound as <c>Count</c>, R361).</summary>
    public int Count { get; set; }

    /// <summary>Whether this provider reports a balance at all (bound as <c>BalanceSupported</c>).</summary>
    public bool BalanceSupported { get; set; }

    /// <summary>True while a balance fetch is in flight (bound as <c>IsFetchingBalance</c>).</summary>
    public bool IsFetchingBalance { get; set; }

''' + anchor2
assert anchor2 in t2 and 'public int Count { get; set; }' not in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(anchor2, add2, 1))
print('CaptchaProvider gains Count/BalanceSupported/IsFetchingBalance')
