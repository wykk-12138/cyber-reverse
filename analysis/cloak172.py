import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                 const masked = function toString() {
                   const fake = FAKES.get(this);
                   if (fake !== undefined) return fake;
                   return protoToString.call(this);
                 };
                 asNative(masked, 'toString', 0);
                 FAKES.set(masked, 'function toString() { [native code] }');
                 try {
                   Object.defineProperty(Function.prototype, 'toString',
                     { value: masked, writable: true, configurable: true, enumerable: false });
                 } catch (e) {}'''

new = '''                 // R172: the cloak REFORMATS rather than answering from a table. V8 prints
                 //   function get userAgent() { [native code] }
                 // and the device prints
                 //   function userAgent() {
                 //       [native code]
                 //   }
                 // so a source that matches V8's native shape is rewritten into WebKit's, and an accessor's role
                 // (the `get `/`set ` word) is dropped. Anything else passes through untouched, which is what keeps a
                 // page's own functions printing their own code.
                 const V8_NATIVE = /^(function [^(]*\\(\\)|class [^ ]*) \\{ \\[native code\\] \\}$/;
                 const V8_ACCESSOR = /^function (?:get|set) (?=[^\\s(])/;

                 // a METHOD SHORTHAND, so `'prototype' in Function.prototype.toString` answers false, as the real one
                 // does — hsw's [ctor, prop] sweep records exactly that predicate, ~110 reads per solve
                 const masked = {
                   toString() {
                     const fake = FAKES.get(this);
                     if (fake !== undefined) return fake;

                     const real = protoToString.call(this);
                     const match = V8_NATIVE.exec(real);
                     return match
                       ? match[1].replace(V8_ACCESSOR, 'function ') + ' {\\n    [native code]\\n}'
                       : real;
                   },
                 }.toString;

                 renamed(masked, 'toString');
                 try { Object.defineProperty(masked, 'length',
                   { value: protoToString.length, configurable: true }); } catch (e) {}
                 FAKES.set(masked, 'function toString() {\\n    [native code]\\n}');
                 try {
                   Object.defineProperty(Function.prototype, 'toString',
                     { value: masked, writable: true, configurable: true, enumerable: false });
                 } catch (e) {}'''

if old not in t:
    raise SystemExit("masked toString anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the cloak reformats")
