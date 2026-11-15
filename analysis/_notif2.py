import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    private readonly TextBlock _clock = UiKit.Status();'''
new = '''    private readonly TextBlock _clock = UiKit.Status();

    /// <summary>"N Notifications", as the live popup's header reads (R336).</summary>
    private readonly TextBlock _caption = UiKit.Title("0 Notifications");'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('_caption field declared')
