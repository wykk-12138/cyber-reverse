import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

start = None
for i, line in enumerate(lines):
    if line.strip() == "const guarded = {":
        start = i
        break

if start is None:
    raise SystemExit("guarded start not found")

end = start
while lines[end].strip() != "}.x;":
    end += 1

replacement = [
    "                       // A getter SHORTHAND gives a function with no `prototype`, which is what an accessor",
    "                       // is — but it must be taken through the DESCRIPTOR: reading `{ get x() {} }.x` CALLS the",
    "                       // getter, whose `this` is the object literal, so the brand check fires during bootstrap",
    "                       // (measured: the whole per-name block threw \"Illegal invocation\" and nothing installed).",
    "                       const guarded = Object.getOwnPropertyDescriptor({",
    "                         get x() {",
    "                           if (!(this instanceof G.Navigator)) {",
    "                             throw new TypeError('Illegal invocation');",
    "                           }",
    "                           return current;",
    "                         },",
    "                       }, 'x').get;",
]

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the getter is taken through its descriptor")
