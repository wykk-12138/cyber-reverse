import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\EngineParity.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

start = None
for i, line in enumerate(lines):
    if line.strip() == "const Wrapped = {":
        start = i
        break

if start is None:
    raise SystemExit("wrapper start not found")

end = start
while lines[end].strip() != "}[name];":
    end += 1

body = lines[start + 1:end]          # the shorthand body, keeping indentation
body[0] = body[0].replace("[name](...args) {", "(...args) {")

replacement = [
    "                         // a function EXPRESSION, not a method shorthand: an error constructor must be",
    "                         // constructible, and a shorthand has no [[Construct]] (measured: 'Error is not a",
    "                         // constructor')",
    "                         const Wrapped = function (...args) {",
] + body + ["                         };"]

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the error wrapper is a constructible function expression")
