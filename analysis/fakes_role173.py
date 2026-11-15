import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t = io.open(p, encoding="utf-8").read()

old = "      FAKES.set(fn, 'function ' + name + '() {\\n    [native code]\\n}');"

new = ("      // the device does not write an accessor's role into its source, so `get userAgent` is cloaked as\n"
       "      // `function userAgent() { … }` — the same rewrite the real cloak applies to untouched natives (R172/R173)\n"
       "      const base = name.indexOf('get ') === 0 ? name.slice(4)\n"
       "        : (name.indexOf('set ') === 0 ? name.slice(4) : name);\n"
       "      FAKES.set(fn, 'function ' + base + '() {\\n    [native code]\\n}');")

if old not in t:
    raise SystemExit("fakes anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("an accessor's role is dropped from its cloaked source")
