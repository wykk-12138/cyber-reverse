import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                // R165: the recorded order, applied after the values are in place.
                surfaceBody += NavOrder.ReseatBodyJs(NavOrder.Navigator);

                // R167: the two plain values from the thirteen, on the prototype and masked below.
                surfaceBody += NavigatorLocks.BodyJs();'''

new = '''                // R167: the two plain values from the thirteen, on the prototype and masked below. Installed
                // BEFORE the reseat, because each install appends a property to the prototype and would
                // otherwise land after everything the reseat just ordered (measured: 29/50 with the order broken).
                surfaceBody += NavigatorLocks.BodyJs();

                // R165: the recorded order, applied last among the value writers.
                surfaceBody += NavOrder.ReseatBodyJs(NavOrder.Navigator);'''

if old not in t:
    raise SystemExit("order anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the reseat comes after every install")
