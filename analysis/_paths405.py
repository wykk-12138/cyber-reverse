import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\AppPaths.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    public static string LocalRoot { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), AppName);'''
new = '''    /// <summary>
    /// The real application's local install/cache directory — **read only**. R405: the only reader is the version panel,
    /// which counts cached packages there; nothing in this replica writes under it. Kept separate from
    /// <see cref="DataRoot"/> so "look at the vendor's files" and "write our own" can never be the same call.
    /// </summary>
    public static string LocalRoot { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), AppName);

    /// <summary>Every path this replica writes to. A test asserts they all sit under <see cref="DataRoot"/>.</summary>
    public static IReadOnlyList<string> WritablePaths { get; } = new[]
    {
        Settings, Accounts, Tasks, Proxies, Billing, Solvers, Analytics, Sessions,
        SmartActions, SmartActionUtilities, BackupsDir, LogsDir, BrowserDataDir, ChromiumDir, TelemetryDir,
    };'''
assert old in t and 'WritablePaths' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('WritablePaths added and LocalRoot documented as read-only')
