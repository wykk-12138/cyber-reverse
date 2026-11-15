import io

base = r"C:\Users\wykk\AppData\Local\Cybersole\replica"

# 1) The two modals are reachable now — R83's whole point.
p = base + r"\tests\Cybersole.Tests\UnreachedUiTypesTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '        "SizeCreatorView", "StoreCreatorView",'
if old in t:
    t = t.replace(old, '        // R83 wired both: the two preset pages open these dialogs instead of\n'
                       '        // hand-building their own copies.\n', 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("baseline: both names removed")
else:
    # they may be listed separately
    for name in ("SizeCreatorView", "StoreCreatorView"):
        for pattern in ('        "%s",\n' % name, '        "%s"' % name):
            if pattern in t:
                t = t.replace(pattern, "", 1)
                print("removed", name)
                break
        else:
            print("not found:", name)
    io.open(p, "w", encoding="utf-8", newline="").write(t)

# 2) The guide's unreachable count.
p2 = base + r"\docs\VERDICT.md"
t2 = io.open(p2, encoding="utf-8").read()
old2 = "UI 类 | 89 个，**39 个不可达**"
new2 = "UI 类 | 89 个，**37 个不可达**"
if old2 in t2:
    t2 = t2.replace(old2, new2, 1)
    io.open(p2, "w", encoding="utf-8", newline="").write(t2)
    print("guide: 39 -> 37")
else:
    print("guide anchor missing")
