import io, re

dump = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(dump, encoding="utf-8", errors="replace").read().split("\n")

selection = None
mutation = None
for line in lines:
    body = line.split("  ", 1)[-1]
    if body.startswith('"){id,checkoutUrl'):
        selection = body
    elif body.startswith("mutation { cartLinesUpdate"):
        mutation = body

assert selection and mutation, "documents not found"
print("selection", len(selection), "braces", selection.count("{"), selection.count("}"))
print("mutation ", len(mutation), "braces", mutation.count("{"), mutation.count("}"))

# Raw string literals: neither document contains a double quote, so """...""" is exact.
cs = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyGraphQl.cs",
             encoding="utf-8").read()

start = cs.index("    public const string CartSelection =")
end = cs.index("    /// <summary>\n    /// The cart query as a complete document")

block = (
    '    public const string CartSelection =\n'
    '        """' + selection + '""";\n\n'
    '    /// <summary>The mutation that changes line quantities, verbatim from the image (346 characters).</summary>\n'
    '    public const string CartLinesUpdate =\n'
    '        """' + mutation + '""";\n\n'
)

cs = cs[:start] + block + cs[end:]
io.open(r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyGraphQl.cs",
        "w", encoding="utf-8", newline="").write(cs)
print("constants rewritten verbatim")
