import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\SmartActions.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('    public List<SmartActionFilter> Filters { get; set; } = new();    public List<SmartActionFilter> Filters { get; set; } = new();',
              '    public List<SmartActionFilter> Filters { get; set; } = new();', 1)
t = t.replace('    public string Value { get => _value; set => SetProperty(ref _value, value); }    public string Value { get => _value; set => SetProperty(ref _value, value); }',
              '    public string Value { get => _value; set => SetProperty(ref _value, value); }', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('duplicates on the same line removed')
