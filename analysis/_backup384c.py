import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\ConfigurationStore.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('            SmartActionUtilities = SmartActions.Utilities,', '            SmartActionUtilities = new SmartActionUtilitiesDocument(),', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('utilities snapshot created empty (the live file only carries "groups")')
