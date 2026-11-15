import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\EngineParity.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

start = None
for i, line in enumerate(lines):
    if line.strip() == "const Wrapped = function (...args) {":
        start = i
        break

if start is None:
    raise SystemExit("wrapper start missing")

end = start
while lines[end].strip() != "};":
    end += 1
    if end - start > 60:
        raise SystemExit("wrapper end not found")

replacement = [
    "                         const Wrapped = function (...args) {",
    "                           const error = new.target",
    "                             ? Reflect.construct(Original, args, new.target)",
    "                             : Original(...args);",
    "                           try {",
    "                             const elide = ELIDE;",
    "                             ELIDE = null;",
    "                             let head = '';",
    "                             if (elide && nativeCapture) {",
    "                               try {",
    "                                 nativeCapture(error, elide[0]);",
    "                                 head = elide[1];",
    "                               } catch (e) {}",
    "                             }",
    "                             const body = toJscStack(error.stack);",
    "                             Object.defineProperty(error, 'stack', {",
    "                               value: head ? (body ? head + '\\n' + body : head) : body,",
    "                               writable: true, configurable: true, enumerable: false,",
    "                             });",
    "                           } catch (e) {}",
    "                           return error;",
    "                         };",
]

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the wrapper body is repaired")
