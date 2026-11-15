import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

# The install helper built a getter, then handed the value to MaskTargets' getter builder when available — which
# returned an unguarded getter, so nothing threw. The guard must be built HERE and only renamed by the mask.
old = '''                     try {
                       const M = G.__nativeMask;
                       if (M && M.getter) return M.getter(function () { return v; }, name);
                     } catch (e) {}
                     return getter;'''

new = '''                     // NOTE: the mask may rename this getter, but it must not rebuild it — MaskTargets' helper wraps
                     // the implementation, and a rebuilt getter has no brand check (measured: the first version of
                     // this function returned `M.getter(...)`, and the throw disappeared).
                     return getter;'''

if old not in t:
    raise SystemExit("install tail anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the guard is not rebuilt by the mask")
