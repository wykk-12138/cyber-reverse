import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Services\CheckoutStats.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public void Flush()
    {
        if (_historyPath is null) return;
        try
        {
            var dir = Path.GetDirectoryName(_historyPath);'''

new = '''    public void Flush()
    {
        if (_historyPath is null) return;

        // R130: nothing to persist and nothing on disk means this instance was constructed and thrown
        // away — a probe, a test, a settings page opened and closed. Creating the directory and writing
        // "[]" there is a side effect nobody asked for: it turns a read into a filesystem write, and on
        // a read-only install it turns into an exception swallowed by the catch below.
        if (_events.Count == 0 && !File.Exists(_historyPath)) return;

        try
        {
            var dir = Path.GetDirectoryName(_historyPath);'''

if old not in t:
    raise SystemExit("Flush anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("Flush no longer creates a directory for an empty, absent history")
