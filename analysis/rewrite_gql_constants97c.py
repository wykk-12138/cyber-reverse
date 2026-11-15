import io

dump = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(dump, encoding="utf-8", errors="replace").read().split("\n")

selection = mutation = None
for line in lines:
    body = line.split("  ", 1)[-1]
    if "checkoutUrl,totalQuantity" in body:
        selection = body
    elif body.startswith("mutation { cartLinesUpdate"):
        mutation = body

assert selection and mutation
print("selection:", len(selection), "starts:", repr(selection[:12]), "quotes:", selection.count('"'))
print("mutation :", len(mutation), "quotes:", mutation.count('"'))


def cs_literal(text: str) -> str:
    out = text.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + out + '"'


cs_path = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyGraphQl.cs"
cs = io.open(cs_path, encoding="utf-8").read()

start = cs.index("    public const string CartSelection =")
end = cs.index("    /// <summary>\n    /// The cart query as a complete document")

block = (
    "    public const string CartSelection =\n"
    "        " + cs_literal(selection) + ";\n\n"
    "    /// <summary>The mutation that changes line quantities, verbatim from the image.</summary>\n"
    "    public const string CartLinesUpdate =\n"
    "        " + cs_literal(mutation) + ";\n\n"
)

io.open(cs_path, "w", encoding="utf-8", newline="").write(cs[:start] + block + cs[end:])
print("constants rewritten with escaped quotes")
