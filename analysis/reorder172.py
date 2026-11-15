import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t = io.open(p, encoding="utf-8").read()

# The image's own note: a helper declared further down is in its temporal dead zone. `masked` used `renamed`
# before it existed, so the whole IIFE threw and __nativeMask was never installed — which is why canShare
# disappeared. Move the three helpers above the cloak.
helpers_start = t.find("                 // R171: the image builds its shims from METHOD SHORTHANDS")
helpers_end = t.find("                 G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter };")
if helpers_start < 0 or helpers_end < 0:
    raise SystemExit("helpers block not found")

helpers_end += len("                 G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter };")
helpers = t[helpers_start:helpers_end]

# remove the block from its current place
t = t[:helpers_start] + t[helpers_end:]

# insert it before the cloak
cloak = t.find("                 // R172: the cloak REFORMATS rather than answering from a table.")
if cloak < 0:
    raise SystemExit("cloak anchor not found")

t = t[:cloak] + helpers + "\n\n" + t[cloak:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the helpers now precede the cloak")
