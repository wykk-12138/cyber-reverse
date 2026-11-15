import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding='utf-8').read()

# expose the image's two AYCD button labels + its confirm message
anchor = '''    public bool DisconnectAycd()'''
add = '''    // ------------------------------------------------ copy from the image's locale (R401)

    /// <summary>"Connect" — the AYCD connect button (Settings.Aycd.ConnectButton).</summary>
    public const string AycdConnectLabel = "Connect";

    /// <summary>"Disconnect" — the AYCD disconnect action (Settings.Aycd.Disconnect.Action).</summary>
    public const string AycdDisconnectLabel = "Disconnect";

''' + anchor
assert anchor in t and 'AycdConnectLabel' not in t
t = t.replace(anchor, add, 1)
t = t.replace('        var connect = UiKit.Button("Connect", () =>', '        var connect = UiKit.Button(AycdConnectLabel, () =>', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('AYCD labels added and the connect button wired')
