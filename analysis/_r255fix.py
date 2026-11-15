import io
for path, dup in [
    (r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Profiles.cs',
     '    public string Name { get => _name; set => SetProperty(ref _name, value); }'),
    (r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs',
     '    public ConcurrencySettings Concurrency { get; set; } = new();'),
]:
    t = io.open(path, encoding='utf-8').read()
    before = t.count(dup)
    t = t.replace(dup + dup, dup, 1)
    t = t.replace(dup + '    ' + dup, dup, 1)
    io.open(path, 'w', encoding='utf-8', newline='').write(t)
    print(path.split('\\')[-1], 'dup before', before, 'after', t.count(dup))
