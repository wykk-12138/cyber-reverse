import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>The group this dialog is editing 鈥?the draft (bound as <c>Draft</c>).</summary>'''
if anchor not in t:
    anchor = '''    public TaskGroup Draft => _group;'''
add = '''    // ------------------------------------------------ copy from the image's locale (R396)
    //
    // The dialog's own labels and the link tooltip, verbatim (TaskGroup.* in the string table). The Delays tab had
    // "Monitor delay" / "Error delay" in lower case, which is not what the image shows.

    /// <summary>"Captcha Solving Source" — the captcha tab's first label.</summary>
    public const string CaptchaSourceLabel = "Captcha Solving Source";

    /// <summary>"Select source" — the captcha source combo's placeholder.</summary>
    public const string CaptchaSourceSelect = "Select source";

    /// <summary>"Cloudflare Solver" — the captcha tab's second label.</summary>
    public const string CloudflareSolverLabel = "Cloudflare Solver";

    /// <summary>"Monitor Delay" — the delays tab.</summary>
    public const string MonitorDelayLabel = "Monitor Delay";

    /// <summary>"Error Delay" — the delays tab's second field.</summary>
    public const string ErrorDelayLabel = "Error Delay";

    /// <summary>The link toggle's tooltip.</summary>
    public const string LinkTooltip = "When toggled, both monitor and retry delays will stay the same";

    /// <summary>"Resetting at" — the limits tab.</summary>
    public const string ResettingAtLabel = "Resetting at";

    /// <summary>"Total Checkout Limit" — the limits tab's first field.</summary>
    public const string TotalCheckoutLimitLabel = "Total Checkout Limit";

    /// <summary>"Webhook Filter" — the notifications tab.</summary>
    public const string WebhookFilterLabel = "Webhook Filter";

    /// <summary>"Select webhook(s)" — the filter combo's placeholder.</summary>
    public const string WebhookFilterSelect = "Select webhook(s)";

''' + anchor
assert anchor in t and 'CaptchaSourceLabel' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ten TaskGroup strings added')
