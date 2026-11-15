import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Tasks.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('    public List<string> Events { get; } = new();',
              '    public List<string> Events { get; } = new();\n\n    /// <inheritdoc />\n    System.Collections.Generic.IReadOnlyList<string> Cybersole.Core.Webhooks.IWebhook.Events => Events;')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('explicit interface member added')
