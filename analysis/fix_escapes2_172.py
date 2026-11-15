import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

out = []
for line in lines:
    stripped = line.strip()

    if stripped.startswith("const V8_NATIVE ="):
        # one backslash each: this is a C# raw string, so nothing is unescaped
        line = "                 const V8_NATIVE = /^(function [^(]*\\(\\)|class [^ ]*) \\{ \\[native code\\] \\}$/;"

    elif stripped.startswith("const V8_ACCESSOR ="):
        line = "                 const V8_ACCESSOR = /^function (?:get|set) (?=[^\\s(])/;"

    elif "match[1].replace(V8_ACCESSOR, 'function ')" in line:
        line = ("                       ? match[1].replace(V8_ACCESSOR, 'function ') + "
                "' {\\n    [native code]\\n}'")

    elif "FAKES.set(masked, 'function toString()" in line:
        line = "                 FAKES.set(masked, 'function toString() {\\n    [native code]\\n}');"

    out.append(line)

io.open(p, "w", encoding="utf-8", newline="").write("\n".join(out))
print("the raw-string lines now carry single backslashes")
