import io, re
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\ConfigurationStore.cs"
t = io.open(p, encoding='utf-8').read()
start = t.index('public sealed class BackupDocument')
end = t.index('\n}', t.index('public AnalyticsDocument Analytics', start)) + 2
block = t[start:end]
# STJ attributes are ignored by Newtonsoft, which is what this project serialises with
block = block.replace('[System.Text.Json.Serialization.JsonPropertyName(', '[Newtonsoft.Json.JsonProperty(')
t = t[:start] + block + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('attributes switched to Newtonsoft')
