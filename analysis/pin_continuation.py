import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            var files = await sp.OpenFilePickerAsync(new Avalonia.Platform.Storage.FilePickerOpenOptions
            {
                Title = "Choose a notification sound",
                AllowMultiple = false,
                FileTypeFilter = new[]
                {
                    new Avalonia.Platform.Storage.FilePickerFileType("Sound files")
                    {
                        Patterns = new[] { "*.wav", "*.mp3" },
                    },
                },
            });'''
new = '''            var files = await sp.OpenFilePickerAsync(new Avalonia.Platform.Storage.FilePickerOpenOptions
            {
                Title = "Choose a notification sound",
                AllowMultiple = false,
                FileTypeFilter = new[]
                {
                    new Avalonia.Platform.Storage.FilePickerFileType("Sound files")
                    {
                        Patterns = new[] { "*.wav", "*.mp3" },
                    },
                },
            }).ConfigureAwait(true);'''
if old not in t:
    raise SystemExit("picker anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("continuation pinned")
