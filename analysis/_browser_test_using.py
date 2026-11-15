import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CustomBrowserTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Cybersole.Services.Localization;', 'using Avalonia.Controls;\nusing Cybersole.Services.Localization;', 1)
t = t.replace('Assert.IsType<DockPanel>(chrome);', 'Assert.IsType<Avalonia.Controls.DockPanel>(chrome);')
t = t.replace('var buttons = ((DockPanel)chrome).Children.OfType<StackPanel>()', 'var buttons = ((Avalonia.Controls.DockPanel)chrome).Children.OfType<Avalonia.Controls.StackPanel>()')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('usings fixed')
