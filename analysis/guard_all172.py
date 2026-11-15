import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public static IReadOnlyList<(string Name, string Body)> AllBodies() => new[]
    {
        ("WebAssembly", WebAssemblySurface.BodyJs()),
        ("Mobile", MobileSurface.BodyJs()),
        ("Engine", MobileSurface.EngineBodyJs()),
        ("Touches", MobileNavigator.BodyJs(SampleAgent)),
        ("WebAssembly wrapper", WebAssemblySurface.ToJavaScript()),
    };'''

new = '''    public static IReadOnlyList<(string Name, string Body)> AllBodies() => new[]
    {
        ("Mask", NativeMask.BodyJs()),
        ("WebAssembly", WebAssemblySurface.BodyJs()),
        ("Mobile", MobileSurface.BodyJs()),
        ("Engine", MobileSurface.EngineBodyJs()),
        ("Touches", MobileNavigator.BodyJs(SampleAgent)),
        ("Prune", NavPrune.BodyJs()),
        ("AudioSession", NavPrune.AudioSessionBodyJs()),
        ("Share", ForwardingShims.WebShareBodyJs()),
        ("Credentials", ForwardingShims.CredentialsBodyJs()),
        ("Reseat", NavOrder.ReseatBodyJs(NavOrder.Navigator)),
        ("MaskTargets", MaskTargets.ApplyJs()),
        ("WebAssembly wrapper", WebAssemblySurface.ToJavaScript()),
    };'''

if old not in t:
    raise SystemExit("allbodies anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the guard now covers all twelve bodies")
