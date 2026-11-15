import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    public static readonly IReadOnlyDictionary<string, (string Title, string Subtitle)> PageHeaders =")
end = t.find("    /// <summary>The header a section prints")
if start < 0 or end < 0:
    raise SystemExit("PageHeaders block not found")

new_block = '''    public static readonly IReadOnlyDictionary<string, (string Title, string Subtitle)> PageHeaders =
        new Dictionary<string, (string, string)>(StringComparer.OrdinalIgnoreCase)
        {
            // R74 read four pages; R75 swept the other eleven in one pass. Every page now has the
            // header the live build prints, word for word.
            ["general"] = ("General", "Profile, delays, and other general preferences"),
            ["appearance"] = ("Appearance", "Customize scrollbar appearance and sizing"),
            ["notifications"] = ("Notifications", "Notifications and sounds"),
            ["webhooks"] = ("Webhooks", "Receive real time notifications into your favorite services"),
            ["email-accounts"] = ("Email Accounts",
                                  "Add imap email accounts to automatically login to certain sites"),
            ["google-accounts"] = ("Google Accounts",
                                   "Store Google accounts for easy access when using solvers"),
            ["paypal-accounts"] = ("PayPal Accounts",
                                   "Store PayPal accounts for easy access when creating tasks"),
            ["data"] = ("Data", "Import, export and backup data"),

            ["captcha-providers"] = ("3rd Party Captcha Providers",
                                     "Add and configure 3rd party captcha solving services"),
            ["cloudflare-solvers"] = ("3rd Party Cloudflare Providers",
                                      "Add Cloudflare solving services, then pick one per task group"),
            ["keyboard-shortcuts"] = ("Keyboard Shortcuts", "Edit and disable keyboard shortcuts"),
            ["custom-stores"] = ("Custom Stores", "Add custom Shopify store presets for easy access"),
            ["custom-sizes"] = ("Custom Sizes", "Add custom Shopify size presets for easy access"),
            ["payment"] = ("Payment", "Configure advanced payment settings"),
            ["need-help"] = ("Get Help", "Take a look at common errors or contact support"),
        };

    /// <summary>
    /// The three rail entries whose page carries a different title. Kept as a set so a test can
    /// assert the count: if a future round "tidies" one of them into agreement, this list shrinks
    /// and so should the test, deliberately.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> RailAndPageDisagree =
        new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["captcha-providers"] = "3rd Party Captcha Providers",
            ["cloudflare-solvers"] = "3rd Party Cloudflare Providers",
            ["need-help"] = "Get Help",
        };

    /// <summary>
    /// The count caption each list-shaped page prints above its rows. The original's wording is
    /// per page, not one shared "{0} items": "0 Presets" for stores, "0 Custom Sizes" for sizes,
    /// "0 Accounts" for the three account pages.
    /// </summary>
    public static string ListCountCaption(string sectionId, int count) => sectionId switch
    {
        "custom-stores" => $"{count} Presets",
        "custom-sizes" => $"{count} Custom Sizes",
        "email-accounts" or "google-accounts" or "paypal-accounts" => $"{count} Accounts",
        _ => count.ToString(),
    };

'''

t = t[:start] + new_block + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("PageHeaders filled: %d sections" % new_block.count('("'))
