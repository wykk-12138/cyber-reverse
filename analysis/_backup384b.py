import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\ConfigurationStore.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('''            Version = "5.18.32",
            CreatedUtc = DateTime.UtcNow,
            Settings = Settings,''', '''            Settings = Settings,''')
t = t.replace('''                Version = "5.18.32",
                CreatedUtc = DateTime.UtcNow,
                Settings = Settings,''', '''                Settings = Settings,''')
# the snapshot should carry the utilities document too, now that it exists
t = t.replace('''            Analytics = Analytics,
            SmartActions = SmartActions,''', '''            Analytics = Analytics,
            SmartActions = SmartActions,
            SmartActionUtilities = SmartActions.Utilities,''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Version/CreatedUtc gone; utilities carried')
