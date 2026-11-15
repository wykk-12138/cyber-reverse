import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\EngineParity.cs"
t = io.open(p, encoding="utf-8").read()

# Error constructors and Array must be CONSTRUCTIBLE: a method shorthand has no [[Construct]], so
# `new Error('x')` answered "Error is not a constructor" (measured, R179). Plain function expressions here.
old1 = '''                     const ArrayWrapped = {
                       Array(...args) {'''
new1 = '''                     const ArrayWrapped = function Array(...args) {'''
if old1 not in t:
    raise SystemExit("array wrapper anchor missing")
t = t.replace(old1, new1, 1)

t = t.replace('''                         return Reflect.construct(RealArray, args, new.target || RealArray);
                       },
                     }.Array;''',
'''                       return Reflect.construct(RealArray, args, new.target || RealArray);
                     };''', 1)

old2 = '''                         const Wrapped = {
                           [name](...args) {'''
new2 = '''                         // a function EXPRESSION, not a shorthand: an error constructor must be constructible, and a
                         // method shorthand has no [[Construct]]
                         const Wrapped = function (...args) {'''
if old2 not in t:
    raise SystemExit("error wrapper anchor missing")
t = t.replace(old2, new2, 1)

t = t.replace('''                             return error;
                           },
                         }[name];''',
'''                           return error;
                         };''', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("both wrappers are constructible")
