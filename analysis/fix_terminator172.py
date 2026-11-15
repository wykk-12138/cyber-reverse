import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

for i, line in enumerate(lines):
    if line.strip() == "})();":
        # the raw-string terminator was removed by an earlier edit; put it back
        if lines[i + 1].strip() != '""";':
            lines.insert(i + 1, '               """;')
        break

io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the raw string is terminated again")
