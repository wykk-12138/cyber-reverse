import io

t = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyFlow.cs",
            encoding="utf-8").read()
lines = t.split("\n")

out = []
for i, l in enumerate(lines[120:210], 121):
    out.append("%4d %s" % (i, l[:130]))

io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\shopify_flow_slice.txt", "w",
        encoding="utf-8", newline="").write("\n".join(out))
print("lines:", len(lines))
