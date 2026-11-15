import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                         get x() {
                           if (!(this instanceof G.Navigator)) {
                             throw new TypeError('Illegal invocation');
                           }
                           return current;
                         },'''

new = '''                         get x() {
                           // A realm-independent brand check: `this instanceof G.Navigator` is FALSE for a child
                           // frame's navigator, because a child realm has its own constructors — so a replayed
                           // accessor threw "Illegal invocation" at the child's own navigator (measured, R174).
                           // The tag is the same string in every realm, and a foreign {} answers [object Object].
                           let tag;
                           try { tag = Object.prototype.toString.call(this); } catch (e) { tag = ''; }
                           if (tag !== '[object Navigator]') {
                             throw new TypeError('Illegal invocation');
                           }
                           return current;
                         },'''

if old not in t:
    raise SystemExit("guard anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the brand check is realm-independent")
