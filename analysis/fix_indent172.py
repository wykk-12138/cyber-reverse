import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

# lines 157..161 (1-based) carry inconsistent indentation inside a raw string literal, which C# rejects:
# every line of a raw string must start at or beyond the closing delimiter's column.
start = 156  # 0-based index of line 157
end = 161    # 0-based index of line 161 ("  })();")

replacement = [
    "                 // exported last: everything above must exist first — the same temporal-dead-zone rule the",
    "                 // image's own note states, and the rule this round broke twice.",
    "                 G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter };",
    "",
    "               })();",
]

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the raw string is consistently indented")
