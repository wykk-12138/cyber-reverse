import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                       const getter = {
                         get [name]() {},
                       };
                       void getter;

                       const fn = Object.getOwnPropertyDescriptor(
                         { get value() { return current; } }, 'value').get;

                       const guarded = {'''

new = '''                       // a getter SHORTHAND: a function with no `prototype`, which is what an accessor is
                       const guarded = {'''

if old not in t:
    raise SystemExit("dead-code anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the body is trimmed to what it does")
