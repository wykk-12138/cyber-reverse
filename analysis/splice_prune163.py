import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                surfaceBody += MobileNavigator.BodyJs(userAgent);
            }'''

new = '''                surfaceBody += MobileNavigator.BodyJs(userAgent);

                // R163: and then delete what WebKit never shipped. This runs after the engine block, which is
                // the only order that can work when one of the members to delete is one the engine block just
                // installed for desktop profiles.
                surfaceBody += NavPrune.BodyJs();
            }'''

if old not in t:
    raise SystemExit("mobile gate anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the prune runs after the engine block")
