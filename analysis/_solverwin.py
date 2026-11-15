import io

# 1) SolverWindow.Dispose + Minimise (it is a Window; Dispose should stop the queue poll if any)
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Captcha\SolverWindow.cs"
import os
if not os.path.exists(p1):
    hits = [l.split('|')[0] for l in os.popen('findstr /S /M /C:"class SolverWindow" src\\Cybersole.Ui\\*.cs').read().split()]
    print('locate:', hits)
else:
    t = io.open(p1, encoding='utf-8').read()
    anchor = '''    private readonly AppServices _services;'''
    add = '''    /// <summary>Minimises the solver window (bound as <c>Minimise</c>).</summary>
    public void Minimise() => WindowState = WindowState.Minimized;

'''
    if 'public void Minimise()' not in t:
        t = t.replace(anchor, add + anchor, 1)
        print('SolverWindow.Minimise added')
    # Dispose: Window already implements IDisposable via Avalonia; expose an explicit method that closes
    anchor2 = '''    public void Minimise() => WindowState = WindowState.Minimized;'''
    add2 = '''
    /// <summary>
    /// Releases the window (bound as <c>Dispose</c>). Avalonia's Window is already disposable; this makes the bound name
    /// exist and closes the window first so a caller sees the same result either way.
    /// </summary>
    public new void Dispose()
    {
        Close();
        base.Dispose();
    }
'''
    if 'public new void Dispose()' not in t:
        t = t.replace(anchor2, anchor2 + add2, 1)
        print('SolverWindow.Dispose added')
    io.open(p1, 'w', encoding='utf-8', newline='').write(t)
