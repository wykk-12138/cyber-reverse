import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# The R76 patch cut from the wrong anchor ("Content = UiKit.Scroll(UiKit.Form(" matched
# GeneralSettingsView's own line, not KeyBindsView's) and took AppearanceView, NotificationsView
# and KeyBindsView with it. Splice a rebuilt block over the damage.
start_marker = "        // The original's whole page-level control is one switch: \"Enable Keyboard Shortcuts\"."
end_marker = "/// Email accounts (Cybersole.Ui.Views.Settings.ImapView)"

start = t.find(start_marker)
end = t.find(end_marker)
if start < 0 or end < 0:
    # ImapView's doc comment may word it differently; fall back to the class declaration.
    end = t.find("public sealed class ImapView : UserControl")
    # back up over its doc comment
    if end > 0:
        doc = t.rfind("///", max(0, end - 2000), end)
        if doc > 0:
            end = t.rfind("\n", 0, doc) + 1

if start < 0 or end <= start:
    raise SystemExit("splice markers not found (%d, %d)" % (start, end))

block = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\r76_repair_block.cs.txt",
                encoding="utf-8").read()

t = t[:start] + block + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("spliced; file is now %d chars" % len(t))
