import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\SplashWindow.cs'
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>How long the splash stays even when start-up is instant.</summary>
    public static readonly TimeSpan MinimumVisible = TimeSpan.FromMilliseconds(700);'''
new = '''    /// <summary>
    /// How long the splash stays even when start-up is instant. Measured on the running build (R220): the window is up
    /// from 607 ms and still up at 4351 ms, i.e. it follows start-up rather than a fixed timer. The floor only stops a
    /// fast start from flashing it; the exit is the shell's <c>Opened</c> event.
    /// </summary>
    public static readonly TimeSpan MinimumVisible = TimeSpan.FromMilliseconds(1200);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('MinimumVisible 700 -> 1200 ms')
