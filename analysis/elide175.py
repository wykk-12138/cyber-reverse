import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\AccessorBrandCheck.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                 const P = G.Navigator && G.Navigator.prototype;
                 if (P) {'''

new = '''                 const P = G.Navigator && G.Navigator.prototype;

                 // R175: a native brand check throws from INSIDE the engine, so its stack has no JS frame for the
                 // check at all — the top frame is the accessor itself, rendered `get userAgent@[native code]`, and
                 // the next is the caller. Ours was built in JS, so the stack carried the override's own frame at
                 // this script's URL, with a line and column. That is a fingerprint readable without any reference
                 // device.
                 //
                 // Captured ONCE, here: reading Error.captureStackTrace at throw time would call whatever the page has
                 // installed on it, announcing every brand-check throw and handing the probe a live reference to the
                 // installed getter as its second argument.
                 const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;

                 const illegalInvocation = (getter, name) => {
                   const err = new TypeError('Illegal invocation');
                   try {
                     if (nativeCapture) {
                       // drop every frame above and including the getter, then put a native-looking frame on top
                       nativeCapture(err, getter);
                       const lines = String(err.stack === undefined ? '' : err.stack).split('\\n');
                       if (lines.length && lines[0].indexOf('Illegal invocation') >= 0) {
                         lines.splice(1, 0, '    at get ' + name + ' (native)');
                         err.stack = lines.join('\\n');
                       }
                     }
                   } catch (e) {}
                   return err;
                 };

                 if (P) {'''

if old not in t:
    raise SystemExit("P anchor missing")
t = t.replace(old, new, 1)

# the getter now throws through the helper
old2 = '''                         get x() {
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

new2 = '''                         get x() {
                           // A realm-independent brand check: `this instanceof G.Navigator` is FALSE for a child
                           // frame's navigator, because a child realm has its own constructors — so a replayed
                           // accessor threw "Illegal invocation" at the child's own navigator (measured, R174).
                           // The tag is the same string in every realm, and a foreign {} answers [object Object].
                           let tag;
                           try { tag = Object.prototype.toString.call(this); } catch (e) { tag = ''; }
                           if (tag !== '[object Navigator]') {
                             throw illegalInvocation(arguments.callee, name);
                           }
                           return current;
                         },'''

if old2 not in t:
    raise SystemExit("getter anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the throw goes through the stack-eliding helper")
