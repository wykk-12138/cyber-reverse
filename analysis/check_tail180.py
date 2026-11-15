import io

# the class tail got mangled; check and repair the doc comment before SymbolRule
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\KeyOrderTable.cs"
t = io.open(p, encoding="utf-8").read()

i = t.find("    /// <summary>Why the symbol guard had to go.</summary>")
print(t[i - 400:i + 400])
