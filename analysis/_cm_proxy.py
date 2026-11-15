import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\Checkout.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>The profiles the form offers (bound as <c>Profiles</c>).</summary>'''
add = '''    /// <summary>The proxy group chosen, when one is (bound as <c>ProxyGroup</c>).</summary>
    public ProxyGroup? ProxyGroup { get; set; }

''' + anchor
assert anchor in t and 'public ProxyGroup? ProxyGroup' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('CreateModel.ProxyGroup added')
