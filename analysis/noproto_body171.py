import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                 G.__nativeMask = { asNative, maskGetter, maskProps };'''

new = '''                 // R171: the image builds its shims from METHOD SHORTHANDS, not from plain functions:
                 //
                 //   const renamed = (fn, name) => { try { Object.defineProperty(fn, 'name', { value: name || '',
                 //     configurable: true }); } catch (e) { } return fn; };
                 //   const noProtoMethod = (impl, name) => renamed(({ m() { return impl.apply(this, arguments); } }).m, name);
                 //   const noProtoGetter = (impl, name) => renamed(Object.getOwnPropertyDescriptor(
                 //     { get m() { return impl.call(this); } }, 'm').get, name ? 'get ' + name : '');
                 //
                 // The trick is in the syntax: `{ m() {} }.m` is an ordinary function expression in every respect except
                 // that it has NO `prototype` property, which is exactly what a WebIDL operation looks like. `delete
                 // fn.prototype` also works, but a shorthand never creates one.
                 const renamed = (fn, name) => {
                   try { Object.defineProperty(fn, 'name', { value: name || '', configurable: true }); } catch (e) {}
                   return fn;
                 };
                 const noProtoMethod = (impl, name) =>
                   renamed(({ m() { return impl.apply(this, arguments); } }).m, name);
                 const noProtoGetter = (impl, name) =>
                   renamed(Object.getOwnPropertyDescriptor(
                     { get m() { return impl.call(this); } }, 'm').get, name ? 'get ' + name : '');

                 G.__nativeMask = { asNative, maskGetter, maskProps, renamed, method: noProtoMethod, getter: noProtoGetter };'''

if old not in t:
    raise SystemExit("mask export anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the protoless builders are exported")
