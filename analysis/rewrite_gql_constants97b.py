import io

dump = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(dump, encoding="utf-8", errors="replace").read().split("\n")

selection = mutation = None
for line in lines:
    body = line.split("  ", 1)[-1]
    if body.startswith("){id,checkoutUrl"):
        selection = body
    elif body.startswith("mutation { cartLinesUpdate"):
        mutation = body

assert selection and mutation

for name, text in (("selection", selection), ("mutation", mutation)):
    assert '"' not in text, name + " contains a quote"
    print(name, len(text), "quotes:", text.count('"'))

cs_path = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyGraphQl.cs"
cs = io.open(cs_path, encoding="utf-8").read()

start = cs.index("    public const string CartSelection =")
end = cs.index("    /// <summary>\n    /// The cart query as a complete document")

block = (
    "    public const string CartSelection =\n"
    '        "' + selection + '";\n\n'
    '    /// <summary>The mutation that changes line quantities, verbatim from the image (346 characters).</summary>\n'
    "    public const string CartLinesUpdate =\n"
    '        "' + mutation + '";\n\n'
)

io.open(cs_path, "w", encoding="utf-8", newline="").write(cs[:start] + block + cs[end:])
print("constants rewritten as plain literals")
