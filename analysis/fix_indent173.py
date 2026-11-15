import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

# put the inserted lines back at the raw string's indentation (17 spaces)
fixed = []
for line in lines:
    if line.startswith("      const base = name.indexOf('get ')"):
        line = "                     const base = name.indexOf('get ') === 0 ? name.slice(4)"
    elif line.startswith("        : (name.indexOf('set ')"):
        line = "                       : (name.indexOf('set ') === 0 ? name.slice(4) : name);"
    elif line.startswith("      FAKES.set(fn, 'function ' + base"):
        line = "                     FAKES.set(fn, 'function ' + base + '() {\\n    [native code]\\n}');"
    fixed.append(line)

text = "\n".join(fixed)
text = text.replace(
    '                     // `function userAgent() { \u2014 }` \u2014 the same rewrite the real cloak applies to untouched natives (R172/R173)',
    '                     // `function userAgent() { \u2014 }` \u2014 the same rewrite the real cloak applies to untouched natives')
io.open(p, "w", encoding="utf-8", newline="").write(text)
print("indentation restored")
