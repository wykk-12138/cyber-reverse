import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileNavigator.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                     try {
                       Object.defineProperty(P && 'languages' in P ? P : N, 'languages',
                         { value: Object.freeze(['__LANGUAGE__']), writable: false,
                           configurable: true, enumerable: true });
                     } catch (e) {}'''

new = '''                     try {
                       const list = Object.freeze(['__LANGUAGE__']);
                       [P, N].forEach((target) => {
                         if (!target) return;
                         try {
                           Object.defineProperty(target, 'languages',
                             { value: list, writable: false, configurable: true, enumerable: true });
                         } catch (e) {}
                       });
                     } catch (e) {}'''

if old not in t:
    raise SystemExit("languages anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("languages tries both targets too")
