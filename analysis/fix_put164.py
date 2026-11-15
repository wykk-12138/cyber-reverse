import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileNavigator.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                     const put = (name, v) => {
                       try {
                         const target = (P && name in P) ? P : N;
                         if (target[name] === v) return;
                         Object.defineProperty(target, name,
                           { value: v, writable: true, configurable: true, enumerable: true });
                       } catch (e) {}
                     };'''

new = '''                     // R164: try the prototype first, then the instance, and verify by reading back. A
                     // defineProperty can be accepted and still be ineffective — the browser's own accessor may
                     // answer from the instance — so the check is the read, not the absence of a throw.
                     const put = (name, v) => {
                       const targets = [P, N];
                       for (var i = 0; i < targets.length; i++) {
                         const target = targets[i];
                         if (!target) continue;
                         try {
                           Object.defineProperty(target, name,
                             { value: v, writable: true, configurable: true, enumerable: true });
                           if (N[name] === v) return;
                         } catch (e) {}
                       }
                     };'''

if old not in t:
    raise SystemExit("put anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("put tries both targets and verifies the read")
