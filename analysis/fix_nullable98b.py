import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyFlow.cs"
t = io.open(p, encoding="utf-8").read()

# StepOutcome is a struct, so the nullable is Nullable<StepOutcome> and `!` does not unwrap it.
old = "            if (graph is not null) return graph!;"
new = "            if (graph is not null) return graph.Value;"

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("return graph.Value")
