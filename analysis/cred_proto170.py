import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ForwardingShims.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                   // no writable/configurable/enumerable in the descriptor: the defaults are false, which is what the
                   // device's own property has
                   Object.defineProperty(nav, 'credentials', { value: shim });'''

new = '''                   // The prototype member stays too, as the image says: "The prototype member stays, so
                   // getOwnPropertyNames(Navigator.prototype) keeps the device's 41 names." This engine has no
                   // container on the prototype at all, so one is defined before the own property shadows it.
                   const proto = Object.getPrototypeOf(nav);
                   if (proto && !('credentials' in proto)) {
                     try {
                       Object.defineProperty(proto, 'credentials',
                         { value: shim, writable: true, configurable: true, enumerable: true });
                     } catch (e) {}
                   }

                   // no writable/configurable/enumerable in the descriptor: the defaults are false, which is what the
                   // device's own property has
                   Object.defineProperty(nav, 'credentials', { value: shim });'''

if old not in t:
    raise SystemExit("credentials define anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the prototype keeps its member")
