import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t = io.open(p, encoding="utf-8").read()

line = "  G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter };"

if line not in t:
    raise SystemExit("assignment line not found")

# remove it from where it is (before maskGetter/maskProps exist — the same temporal-dead-zone mistake the image
# warns about, made twice in one round)
t = t.replace(line + "\n\n", "", 1)

# and put it at the end of the IIFE, after everything it names has been defined
closing = '''                 G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter };'''

if closing in t:
    t = t.replace(closing, "", 1)

anchor = "                 G.__nativeMask = "
if anchor in t:
    raise SystemExit("stray anchor remains")

# find the end of the IIFE: the last "})();" in the raw string
idx = t.rfind("})();")
if idx < 0:
    raise SystemExit("IIFE end not found")

insert = ("  // exported last: everything above must exist first, which is the same temporal-dead-zone rule the\n"
          "  // image's own note states — and the rule this round broke twice.\n"
          "  G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter };\n\n  ")

t = t[:idx] + insert + t[idx:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the export happens after everything it names")
