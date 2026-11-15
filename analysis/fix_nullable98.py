import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyFlow.cs"
t = io.open(p, encoding="utf-8").read()

# `if (graph is not null) return graph;` — under nullable analysis StepOutcome? narrows to
# StepOutcome?, so return graph! (the null check above is the guard).
old = "            if (graph is not null) return graph;"
new = "            if (graph is not null) return graph!;"

if old not in t:
    raise SystemExit("return anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("nullable return fixed")
