import io

# 1) inside a C# raw string there is no escape processing, so the JS must carry single backslashes
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t1 = io.open(p1, encoding="utf-8").read()

t1 = t1.replace(
    "const V8_NATIVE = /^(function [^(]*\\\\(\\\\)|class [^ ]*) \\\\{ \\\\[native code\\\\] \\\\}$/;",
    "const V8_NATIVE = /^(function [^ (]*\\(\\)|class [^ ]*) \\{ \\[native code\\] \\}$/;"
    .replace("function [^ (]*", "function [^(]*"))

t1 = t1.replace(
    "const V8_ACCESSOR = /^function (?:get|set) (?=[^\\\\s(])/;",
    "const V8_ACCESSOR = /^function (?:get|set) (?=[^\\s(])/;")

t1 = t1.replace(
    "? match[1].replace(V8_ACCESSOR, 'function ') + ' {\\\\n    [native code]\\\\n}'",
    "? match[1].replace(V8_ACCESSOR, 'function ') + ' {\\n    [native code]\\n}'")

t1 = t1.replace(
    "FAKES.set(masked, 'function toString() {\\\\n    [native code]\\\\n}');",
    "FAKES.set(masked, 'function toString() {\\n    [native code]\\n}');")

io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) the guard must not report an escape that sits inside a string literal
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        // 1. a literal backslash-n means someone escaped a newline twice; outside a string it is a syntax error
        if (js.Contains("\\\\n", System.StringComparison.Ordinal))
            problems.Add(new Problem("literal-\\\\n", "a literal backslash-n survived into the body"));

        if (js.Contains("\\\\t", System.StringComparison.Ordinal))
            problems.Add(new Problem("literal-\\\\t", "a literal backslash-t survived into the body"));'''

new2 = '''        // 1. A literal backslash-n OUTSIDE a string literal means someone escaped a newline twice; inside one it is
        //    ordinary JavaScript. The distinction is why this is a scan and not a Contains (R172).
        foreach (var escape in EscapesOutsideStrings(js))
            problems.Add(new Problem("literal-" + escape, "an escape survived into code position: " + escape));'''

if old2 not in t2:
    raise SystemExit("guard escape anchor missing")
t2 = t2.replace(old2, new2, 1)

# add the scanner next to the delimiter counter
anchor = "    /// <summary>\n    /// Net delimiter balance, skipping string literals and comments so a <c>'{'</c> inside a string does not count.\n    /// </summary>"
scanner = '''    /// <summary>
    /// Backslash escapes that appear in code position rather than inside a string or comment.
    /// </summary>
    private static IReadOnlyList<string> EscapesOutsideStrings(string js)
    {
        var found = new List<string>();
        char quote = '\\0';

        for (var i = 0; i < js.Length - 1; i++)
        {
            var c = js[i];

            if (quote != '\\0')
            {
                if (c == '\\\\') { i++; continue; }
                if (c == quote) quote = '\\0';
                continue;
            }

            if (c == '/' && js[i + 1] == '/')
            {
                while (i < js.Length && js[i] != '\\n') i++;
                continue;
            }

            if (c == '\\'' || c == '"' || c == '`') { quote = c; continue; }

            if (c == '\\\\' && js[i + 1] is 'n' or 't')
            {
                var name = "\\\\" + js[i + 1];
                if (!found.Contains(name)) found.Add(name);
                i++;
            }
        }

        return found;
    }

''' + anchor

if anchor not in t2:
    raise SystemExit("delimiter doc anchor missing")
t2 = t2.replace(anchor, scanner, 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("raw-string escapes fixed; the guard scans code position")
