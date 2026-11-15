import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Section("3D Secure",
                UiKit.Row("Auto Open 3DS", auto3ds),
                // R195: AutoOpen3DSLimit had no control. The property existed, MainWindow read it
                // to cap how many 3DS windows open at once, and the value was whatever the default
                // said — 5 — forever. The original has two fields here, not one:
                //
                //   Settings.Payment.AutoOpen3DS       "Auto Open 3DS"
                //   Settings.Payment.AutoOpen3DSLimit  "Max Open"
                //      tooltip: Maximum number of 3DS windows opened automatically at once.
                UiKit.Row("Max Open", auto3dsLimit)),
            UiKit.Section("External Browser",
                UiKit.Row("Browser Path", UiKit.Buttons(browserPath, configure)),
                UiKit.Row("Maximum Browser Tabs", browserTabs),
                UiKit.Row("Open Link As", openAs)),
            UiKit.Section("Browser Profiles",
                UiKit.Row("Checkout Profiles", UiKit.Buttons(checkoutProfile, refreshProfiles)),
                UiKit.Row("Profile Assignment", assignment)),'''

new = '''        // R77: the live page prints its three headings as dim captions, not as bold card titles
        // (the same correction R75 made on five other pages), and at rest it shows six controls.
        Content = UiKit.Scroll(UiKit.Form(
            UiKit.PlainCard(
                UiKit.Caption("3D Secure"),
                UiKit.Row("Auto Open 3DS", auto3ds),
                // R195: AutoOpen3DSLimit had no control. The property existed, MainWindow read it
                // to cap how many 3DS windows open at once, and the value was whatever the default
                // said — 5 — forever. The original has two fields here, not one:
                //
                //   Settings.Payment.AutoOpen3DS       "Auto Open 3DS"
                //   Settings.Payment.AutoOpen3DSLimit  "Max Open"
                //      tooltip: Maximum number of 3DS windows opened automatically at once.
                //
                // R77 caveat: the live page at rest shows only "Auto Open 3DS" — this second row
                // is not on it. Either it appears only when Auto Open 3DS is Yes, or the label is
                // an orphan. The combo could not be driven to find out (see PaymentView.LiveControls
                // and docs/SESSION_STATE.md), so the row stays: the property is real, MainWindow
                // reads it, and hiding it would strand the value with no editor.
                UiKit.Row("Max Open", auto3dsLimit)),
            UiKit.PlainCard(
                UiKit.Caption("External Browser"),
                UiKit.Row("Browser Path", UiKit.Buttons(browserPath, configure)),
                UiKit.Row("Maximum Browser Tabs", browserTabs),
                UiKit.Row("Open Link As", openAs)),
            UiKit.PlainCard(
                UiKit.Caption("Browser Profiles"),
                UiKit.Row("Checkout Profiles", UiKit.Buttons(checkoutProfile, refreshProfiles)),
                UiKit.Row("Profile Assignment", assignment)),'''

if old not in t:
    raise SystemExit("payment content anchor missing")
t = t.replace(old, new, 1)

# The evidence table, next to the class.
anchor = "/// <summary>Payment / 3-D Secure settings (Cybersole.Ui.Views.Settings.PaymentView).</summary>\npublic sealed class PaymentView : UserControl\n{"
table = '''/// <summary>Payment / 3-D Secure settings (Cybersole.Ui.Views.Settings.PaymentView).</summary>
public sealed class PaymentView : UserControl
{
    /// <summary>
    /// The controls the live page shows at rest, in its order, read off the running build in R77.
    ///
    /// <para>
    /// Six of them, in three sections:
    /// </para>
    ///
    /// <code>
    /// 3D Secure         Auto Open 3DS                     [No]
    /// External Browser  Browser Path                      [None] [Configure]
    ///                   Maximum Browser Tabs              [10]
    ///                   Open Link As                      [Tab]
    /// Browser Profiles  Checkout Profiles                 [Browser default] [Refresh]
    ///                   Profile Assignment                [Round robin]
    /// </code>
    ///
    /// <para>
    /// The locale carries a seventh field — <c>Settings.Payment.AutoOpen3DSLimit</c>, "Max Open" —
    /// which the replica renders and the live page does not show at rest. Whether it is conditional
    /// on Auto Open 3DS or simply has no control is <b>unresolved</b>: the live build's combo boxes
    /// expose no accessibility peer and a click does not open their popup, so the value could not be
    /// switched to find out.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> LiveControls = new[]
    {
        "Auto Open 3DS",
        "Browser Path",
        "Maximum Browser Tabs",
        "Open Link As",
        "Checkout Profiles",
        "Profile Assignment",
    };

    /// <summary>The three section headings, in the live page's order.</summary>
    public static readonly IReadOnlyList<string> LiveSections = new[]
    {
        "3D Secure", "External Browser", "Browser Profiles",
    };

'''
if anchor not in t:
    raise SystemExit("PaymentView class anchor missing")
t = t.replace(anchor, table, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("PaymentView aligned with the live page")
