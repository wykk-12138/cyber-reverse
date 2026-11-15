import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Store\AppPaths.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    public const string AppName = "Cybersole";

    public static string DataRoot { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), AppName);'''
new = '''    public const string AppName = "Cybersole";

    /// <summary>
    /// Where this replica keeps its JSON. **Deliberately not the original's directory.**
    ///
    /// <para>
    /// R387: this used to be <c>%APPDATA%\\Cybersole</c> — the same folder the real 5.18.32 writes. Two consequences, both
    /// bad: running the replica overwrote the user's live configuration, and every "does my model match the original's
    /// file?" check became circular, because the file it read may have been written by the replica itself. The default is
    /// now <c>%APPDATA%\\CybersoleReplica</c>; <c>CYBERSOLE_DATA_ROOT</c> overrides it for tests.
    /// </para>
    /// </summary>
    public static string DataRoot { get; } =
        Environment.GetEnvironmentVariable("CYBERSOLE_DATA_ROOT") is { Length: > 0 } overridden
            ? overridden
            : Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), AppName + "Replica");

    /// <summary>The directory the real application uses — read-only evidence, never written here.</summary>
    public static string OriginalDataRoot { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), AppName);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('DataRoot moved off the original directory')
