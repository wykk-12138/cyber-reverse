import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# 1) remove the call from the top of apply
old_call = '''            // The engine surface is part of the realm patch, because a challenge frame reads
            // WebAssembly itself rather than asking its parent (R146/R148).
            __SURFACE_CALL__
'''
if old_call not in t:
    raise SystemExit("early call anchor missing")
t = t.replace(old_call, "", 1)

# 2) put it at the end of apply: the engine block must win over the individual patches above it, which is
#    exactly what R156's runtime measurement showed — three plugins survived because the surface ran first.
old_tail = '''          // The set of realms already patched. A WeakSet rather than a flag on the window: a'''

new_tail = '''            // Last, so it wins: the engine block restates the members the payload reads (five plugins, the
            // connection quartet, the two flags) and has to run after the individual patches above, which
            // R156's browser measurement showed replacing it when it ran first (R156).
            __SURFACE_CALL__
          };

          // The set of realms already patched. A WeakSet rather than a flag on the window: a'''

if old_tail not in t:
    raise SystemExit("apply tail anchor missing")
t = t.replace(old_tail, new_tail, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the surface call moved to the end of apply")
