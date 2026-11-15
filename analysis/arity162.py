import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MaskTargets.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        foreach (var target in Functions)
        {
            js += "      try {\\n";
            js += "        const owner = " + target.Owner + ";\\n";
            js += "        if (owner && typeof owner." + target.Property + " === 'function')\\n";
            js += "          M.asNative(owner." + target.Property + ", '" + target.Property + "',\\n";
            js += "            owner." + target.Property + ".length);\\n";
            js += "      } catch (e) {}\\n";
        }'''

new = '''        foreach (var target in Functions)
        {
            // R162: the arity comes from the platform's signature, not from the shim that replaced it — copying
            // `owner[prop].length` copies the patched function's own length, which is zero for a shim written
            // as `function () {}`.
            var arity = NativeArity.For(target.Property);
            if (arity is null)
                throw new System.InvalidOperationException(
                    "no platform arity recorded for " + target.Property);

            js += "      try {\\n";
            js += "        const owner = " + target.Owner + ";\\n";
            js += "        if (owner && typeof owner." + target.Property + " === 'function')\\n";
            js += "          M.asNative(owner." + target.Property + ", '" + target.Property + "', " +
                  arity.Value + ");\\n";
            js += "      } catch (e) {}\\n";
        }'''

if old not in t:
    raise SystemExit("functions loop anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the arity comes from the table")
