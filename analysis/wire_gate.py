import io

# ---------------------------------------------------------------- 1) master gate + Play
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Services\NotificationService.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var opts = OptionsFor(kind);
        if (!opts.Enabled) return;'''
new = '''        // The page's "Enable Notifications" switch is settings.notifications — a master gate above
        // the five per-category "Allow ... Notifications" switches. R78 found it read by nobody.
        if (!_settings.Notifications) return;

        var opts = OptionsFor(kind);
        if (!opts.Enabled) return;'''
if old not in t:
    raise SystemExit("gate anchor missing")
t = t.replace(old, new, 1)

anchor = "    public NotificationOptions OptionsFor(NotificationKind kind) => kind switch"
play = '''    /// <summary>
    /// Plays a notification sound now — what the Notifications page's Play button does. It routes
    /// through the same player the fan-out uses, so the button demonstrates the real path instead
    /// of a second one that could drift.
    /// </summary>
    public void PlaySound(string? path) => _sound.Play(path);

'''
if anchor not in t:
    raise SystemExit("options anchor missing")
t = t.replace(anchor, play + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("master gate + PlaySound")
