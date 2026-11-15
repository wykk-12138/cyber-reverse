import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# Unique anchors, both asserted — the R76 lesson.
start_marker = "/// <summary>\n/// Notifications (Cybersole.Ui.Views.Settings.NotificationsView)."
end_marker = "/// <summary>\n/// Keyboard Shortcuts (Cybersole.Ui.Views.Settings.KeyBindsView)."

start = t.find(start_marker)
end = t.find(end_marker)

if start < 0:
    raise SystemExit("notifications start anchor not found")
if end < 0:
    raise SystemExit("keybinds start anchor not found")
if end <= start:
    raise SystemExit("anchors out of order: %d .. %d" % (start, end))
# both must be unique
if t.count(start_marker) != 1:
    raise SystemExit("notifications anchor is not unique (%d)" % t.count(start_marker))
if t.count(end_marker) != 1:
    raise SystemExit("keybinds anchor is not unique (%d)" % t.count(end_marker))

block = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\r78_notifications_view.cs.txt",
                encoding="utf-8").read()

# Replace the class but keep the KeyBinds doc comment that starts at end_marker.
t = t[:start] + block + "\n" + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("NotificationsView replaced; removed %d chars, added %d"
      % (end - start, len(block)))
