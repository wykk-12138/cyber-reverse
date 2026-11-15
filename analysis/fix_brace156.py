import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# The move left the original closing brace in place, so the call ended up outside apply — a SyntaxError the
# browser swallows silently. Put the call inside the function and drop the duplicate brace.
old = '''            } catch (e) {}
          };

            // Last, so it wins: the engine block restates the members the payload reads (five plugins, the
            // connection quartet, the two flags) and has to run after the individual patches above, which
            // R156's browser measurement showed replacing it when it ran first (R156).
            __SURFACE_CALL__
          };
'''

new = '''            } catch (e) {}

            // Last, so it wins: the engine block restates the members the payload reads (five plugins, the
            // connection quartet, the two flags) and has to run after the individual patches above, which
            // R156's browser measurement showed replacing it when it ran first.
            __SURFACE_CALL__
          };
'''

if old not in t:
    raise SystemExit("duplicate brace anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the call sits inside apply, with one closing brace")
