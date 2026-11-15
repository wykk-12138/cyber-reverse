import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\SmartActions.cs'
t = io.open(p, encoding='utf-8').read()

filters = '    public List<SmartActionFilter> Filters { get; set; } = new();'
value = '    public string Value { get => _value; set => SetProperty(ref _value, value); }'
t = t.replace(filters + '\n' + filters, filters, 1)
t = t.replace('    ' + filters + '\n' + filters, filters, 1)
t = t.replace(value + '\n' + value, value, 1)
t = t.replace(value + '\n' + '    ' + value, value, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
import re
print('filters decls:', len(re.findall(r'public List<SmartActionFilter> Filters', t)))
print('value decls  :', len(re.findall(r'public string Value \{ get', t)))
