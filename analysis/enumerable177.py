import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the install descriptor follows `enumerable !== false`
old = '''                       Object.defineProperty(P, name,
                         { get: getter, configurable: true, enumerable: true });'''

new = '''                       // `enumerable: enumerable !== false` — true by default, false when a call site says so. The
                       // image's value() takes the parameter and passes it straight through (R177).
                       Object.defineProperty(P, name,
                         { get: getter, configurable: true, enumerable: !MUST_HIDE.has(name) });'''

if old not in t:
    raise SystemExit("define anchor missing")
t = t.replace(old, new, 1)

# 2) the body declares the set, so the expression above can read it
old2 = '''                 const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;
                 let ELIDE = null;'''

new2 = '''                 const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;
                 let ELIDE = null;

                 // the names a call site installs non-enumerable; empty here, because every member this workspace
                 // installs on Navigator.prototype is one the device reports in its for-in walk
                 const MUST_HIDE = new Set([]);'''

if old2 not in t:
    raise SystemExit("capture anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the descriptor follows enumerable !== false")
