import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\ConfigurationStore.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('        var compact = (JsonSerializerSettings)Json.Default;\n        var settings = new JsonSerializerSettings',
              '        var settings = new Newtonsoft.Json.JsonSerializerSettings', 1)
t = t.replace('''            ContractResolver = compact.ContractResolver,
            Formatting = Newtonsoft.Json.Formatting.None,
            NullValueHandling = compact.NullValueHandling,
            DateTimeZoneHandling = compact.DateTimeZoneHandling,
            Converters = compact.Converters,''',
'''            ContractResolver = Json.Default.ContractResolver,
            Formatting = Newtonsoft.Json.Formatting.None,
            NullValueHandling = Json.Default.NullValueHandling,
            DateTimeZoneHandling = Json.Default.DateTimeZoneHandling,
            Converters = Json.Default.Converters,''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('fully qualified')
