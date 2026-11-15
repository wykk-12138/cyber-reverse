import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                       // a getter SHORTHAND: a function with no `prototype`, which is what an accessor is
                       const guarded = {
                         get x() {
                           if (!(this instanceof G.Navigator)) {
                             throw new TypeError('Illegal invocation');
                           }
                           return current;
                         },
                       }.x;'''

new = '''                       // A getter SHORTHAND gives a function with no `prototype`, which is what an accessor is — but
                       // it must be taken through the DESCRIPTOR: reading `{ get x() {} }.x` CALLS the getter, whose
                       // `this` is the object literal, so the brand check fires during bootstrap (measured: the whole
                       // per-name block threw "Illegal invocation" and nothing was installed).
                       const guarded = Object.getOwnPropertyDescriptor({
                         get x() {
                           if (!(this instanceof G.Navigator)) {
                             throw new TypeError('Illegal invocation');
                           }
                           return current;
                         },
                       }, 'x').get;'''

if old not in t:
    raise SystemExit("guarded anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the getter is taken through its descriptor")
