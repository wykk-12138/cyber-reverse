"""Lift PayPalAccountCreatorView's form fields onto bound members (R520).

The audit says this class is missing six bound members:

    AutoReopen / Password / ProxyGroup / UseLoginProxy / Save / Close

Reading the class: it is NOT a stub. The dialog is complete — seven labelled rows, a Save footer, validation,
persistence. What it lacks is *names*: every field is a local in the constructor,

    var model = UiKit.Text(existing?.Email, watermark: "paypal email");
    var password = UiKit.Text(password: true);
    ...

so no binding can address any of them. Same shape as AccountGrid in R508.

What this does:
  * the four widgets the audit names become readonly fields behind writable properties
    (get reads the widget, set writes it — one source of truth, no shadow copy);
  * the save lambda becomes `SaveCore()` so `Save` can be an `ICommand`; `SaveButton` keeps pointing at
    the same code path;
  * `_model` / `_existing` / `_doc` / `_services` become fields because `SaveCore` needs them.

`Close` is NOT added: `SettingsModal` derives from `Window`, whose `Close()` owns the name (CS0102) —
the same hard constraint as MessageBoxDialog.

All substitution happens INSIDE the class body. A first attempt replaced against the whole file and found
`var doc = services.Config.Accounts;` twice (another modal uses the same line), which is exactly the
cross-object damage AGENTS.md §3(g) warns about.
"""

import io
import re

PATH = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
CLS = "PayPalAccountCreatorView"

MEMBERS = '''    // R520: the four widgets the original binds by name. The getter writes through to the widget, so there is no
    // second copy to keep in sync and a later assignment shows up on screen immediately.
    /// <summary>PayPal password (bound as <c>Password</c>).</summary>
    public string Password
    {
        get => _password.Text ?? string.Empty;
        set => _password.Text = value ?? string.Empty;
    }

    /// <summary>Proxy group name (bound as <c>ProxyGroup</c>).</summary>
    public string ProxyGroup
    {
        get => _proxyGroup.Text ?? string.Empty;
        set => _proxyGroup.Text = value ?? string.Empty;
    }

    /// <summary>Whether checkout goes out through the account's login proxy (bound as <c>UseLoginProxy</c>).</summary>
    public bool UseLoginProxy
    {
        get => _useLoginProxy.IsChecked == true;
        set => _useLoginProxy.IsChecked = value;
    }

    /// <summary>Whether the session reopens after a drop (bound as <c>AutoReopen</c>).</summary>
    public bool AutoReopen
    {
        get => _autoReopen.IsChecked == true;
        set => _autoReopen.IsChecked = value;
    }

    /// <summary>Bound as <c>Save</c>: the same body the footer button runs.</summary>
    public ICommand Save { get; }

    private readonly TextBox _model;
    private readonly TextBox _password;
    private readonly TextBox _proxyGroup;
    private readonly CheckBox _useLoginProxy;
    private readonly CheckBox _autoReopen;
    private readonly PayPalAccount? _existing;
    private readonly AccountsDocument _doc;
    private readonly AppServices _services;
'''

SAVE_CORE = '''
    /// <summary>Validates and persists; the footer's Save button and the bound <c>Save</c> both run this.</summary>
    private void SaveCore()
    {
        if (string.IsNullOrWhiteSpace(_model.Text))
            throw new InvalidOperationException("A PayPal email is required.");

        var target = _existing ?? new PayPalAccount();
        target.Email = _model.Text!;
        target.ProxyGroup = _proxyGroup.Text;
        target.UseLoginProxy = _useLoginProxy.IsChecked == true;
        target.AutoReopen = _autoReopen.IsChecked == true;
        target.LastRefresh = DateTime.UtcNow;

        if (_existing is null) _doc.PayPal.Add(target);
        _services.Config.Save();
    }
'''

SWAPS = [
    ("        var doc = services.Config.Accounts;\n",
     "        _services = services;\n        _existing = existing;\n        _doc = services.Config.Accounts;\n"),
    ('        var model = UiKit.Text(existing?.Email, watermark: "paypal email");\n',
     '        _model = UiKit.Text(existing?.Email, watermark: "paypal email");\n'),
    ("        var password = UiKit.Text(password: true);\n",
     "        _password = UiKit.Text(password: true);\n"),
    ('        var proxyGroup = UiKit.Text(existing?.ProxyGroup, watermark: "proxy group");\n',
     '        _proxyGroup = UiKit.Text(existing?.ProxyGroup, watermark: "proxy group");\n'),
    ('        var useLoginProxy = UiKit.Check("Use login proxy", existing?.UseLoginProxy ?? true);\n',
     '        _useLoginProxy = UiKit.Check("Use login proxy", existing?.UseLoginProxy ?? true);\n'),
    ('        var autoReopen = UiKit.Check("Auto reopen", existing?.AutoReopen ?? false);\n',
     '        _autoReopen = UiKit.Check("Auto reopen", existing?.AutoReopen ?? false);\n'),
    ('UiKit.Row("Model", model)', 'UiKit.Row("Model", _model)'),
    ('UiKit.Row("Password", password)', 'UiKit.Row("Password", _password)'),
    ('UiKit.Row("Proxy group", proxyGroup)', 'UiKit.Row("Proxy group", _proxyGroup)'),
    ('UiKit.Row("Use login proxy", useLoginProxy)', 'UiKit.Row("Use login proxy", _useLoginProxy)'),
    ('UiKit.Row("Auto reopen", autoReopen)', 'UiKit.Row("Auto reopen", _autoReopen)'),
]

OLD_FOOTER = """        BuildFooter(SaveButton(() =>
        {
            if (string.IsNullOrWhiteSpace(model.Text))
                throw new InvalidOperationException("A PayPal email is required.");

            var target = existing ?? new PayPalAccount();
            target.Email = model.Text!;
            target.ProxyGroup = proxyGroup.Text;
            target.UseLoginProxy = useLoginProxy.IsChecked == true;
            target.AutoReopen = autoReopen.IsChecked == true;
            target.LastRefresh = DateTime.UtcNow;

            if (existing is null) doc.PayPal.Add(target);
            services.Config.Save();
        }));"""

NEW_FOOTER = """        Save = new RelayCommand(SaveCore);
        BuildFooter(SaveButton(SaveCore));"""


def main():
    text = io.open(PATH, encoding="utf-8").read()

    m = re.search(r"\bclass\s+" + CLS + r"\b", text)
    if not m:
        raise SystemExit("class not found")
    brace = text.find("{", m.end())
    depth, i = 0, brace
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[brace:i]

    ctor = "    public %s(AppServices services, PayPalAccount? existing = null)\n" % CLS
    if body.count(ctor) != 1:
        raise SystemExit("ctor count = %d" % body.count(ctor))
    body = body.replace(ctor, MEMBERS + "\n" + ctor, 1)

    for old, new in SWAPS:
        if body.count(old) != 1:
            raise SystemExit("%r count=%d" % (old.strip()[:50], body.count(old)))
        body = body.replace(old, new, 1)

    if body.count(OLD_FOOTER) != 1:
        raise SystemExit("footer count = %d" % body.count(OLD_FOOTER))
    body = body.replace(OLD_FOOTER, NEW_FOOTER, 1)

    marker = "\n        Save = new RelayCommand(SaveCore);\n        BuildFooter(SaveButton(SaveCore));\n    }\n"
    if body.count(marker) != 1:
        raise SystemExit("marker count = %d" % body.count(marker))
    body = body.replace(marker, marker + SAVE_CORE, 1)

    io.open(PATH, "w", encoding="utf-8").write(text[:brace] + body + text[i:])
    print("PayPalAccountCreatorView: Password / ProxyGroup / UseLoginProxy / AutoReopen / Save wired")


if __name__ == "__main__":
    main()
