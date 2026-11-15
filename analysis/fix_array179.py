import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\EngineParity.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

start = None
for i, line in enumerate(lines):
    if line.strip() == "const ArrayWrapped = {":
        start = i
        break

if start is None:
    raise SystemExit("array start missing")

end = start
while lines[end].strip() != "}.Array;":
    end += 1

replacement = [
    "                     // constructible, for the same reason the error wrappers are",
    "                     const ArrayWrapped = function Array(...args) {",
    "                       if (args.length === 1 && typeof args[0] === 'number'",
    "                           && (args[0] < 0 || args[0] > 4294967295 || args[0] % 1 !== 0)) {",
    "                         throw new RangeError(MESSAGES.badArrayLength);",
    "                       }",
    "                       return Reflect.construct(RealArray, args, new.target || RealArray);",
    "                     };",
]

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("Array is constructible")
