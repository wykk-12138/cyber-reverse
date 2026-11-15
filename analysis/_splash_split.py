import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\SplashWindow.cs'
t = io.open(p, encoding='utf-8').read()

# 1) extract the visual tree into a static builder that needs no Window
old_ctor_tail = '''    public SplashWindow(string? version = null, string? language = null)
    {
        Title = "Cybersole";'''
new_ctor_tail = '''    public SplashWindow(string? version = null, string? language = null)
        : this(BuildVisual(LocalizationService.Translate(language, WelcomeKey), version).Background,
               LocalizationService.Translate(language, WelcomeKey), version)
    {
    }

    private SplashWindow(Border background, string welcome, string? version)
    {
        Title = "Cybersole";'''
assert old_ctor_tail in t
t = t.replace(old_ctor_tail, new_ctor_tail, 1)

# 2) replace the body's visual construction with the built pair
start = t.index('        var loc = new LocalizationService(')
end = t.index('        Background1.Child = stack;')
body = '''        Background1 = background;
'''
t = t[:start] + body + t[end + len('        Background1.Child = stack;\n'):]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ctor split; now add the builder')
