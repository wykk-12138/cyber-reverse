import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                       const current = P[name];
                       if (current === undefined) return;'''

new = '''                       // Reading the value off the PROTOTYPE throws when the platform's own member is an accessor
                       // bound to the interface (measured: `Navigator.prototype.platform` throws Illegal invocation).
                       // So the value is taken from the instance, which is where a Navigator exists.
                       let current;
                       try { current = G.navigator[name]; } catch (e) { current = undefined; }
                       if (current === undefined) {
                         try { current = P[name]; } catch (e) { current = undefined; }
                       }
                       if (current === undefined) return;'''

if old not in t:
    raise SystemExit("current-value anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the value comes from the instance")
