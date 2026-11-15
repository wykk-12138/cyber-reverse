import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NavPrune.cs"
t = io.open(p, encoding="utf-8").read()

old = '''               try {
                 const proto = G.Navigator && G.Navigator.prototype;
                 if (proto) {
                   const keep = new Set([__ALLOWED__]);
                   Object.getOwnPropertyNames(proto).forEach((key) => {
                     if (!keep.has(key) && key !== 'constructor') {
                       try { delete proto[key]; } catch (e) {}
                     }
                   });
                 }
               } catch (e) {}
               """.Replace("__ALLOWED__", allowed);'''

new = '''               try {
                 const keep = new Set([__ALLOWED__]);
                 const sweep = (target) => {
                   if (!target) return;
                   Object.getOwnPropertyNames(target).forEach((key) => {
                     if (!keep.has(key) && key !== 'constructor') {
                       try { delete target[key]; } catch (e) {}
                     }
                   });
                 };

                 // The image sweeps the prototype, because it installs everything there. This replica's own
                 // scripts still put a few members on the instance (deviceMemory among them), so the sweep
                 // runs over both — a superset of the same rule, and the measurement says why: without it an
                 // iPhone profile still answered navigator.deviceMemory.
                 sweep(G.Navigator && G.Navigator.prototype);
                 sweep(G.navigator);
               } catch (e) {}
               """.Replace("__ALLOWED__", allowed);'''

if old not in t:
    raise SystemExit("sweep anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the sweep covers the instance too")
