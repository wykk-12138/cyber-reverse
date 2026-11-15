import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    private static (int Braces, int Parens, int Brackets) CountDelimiters(string js)
    {
        int braces = 0, parens = 0, brackets = 0;
        char quote = '\\0';

        for (var i = 0; i < js.Length; i++)
        {
            var c = js[i];

            if (quote != '\\0')
            {
                if (c == '\\\\') { i++; continue; }
                if (c == quote) quote = '\\0';
                continue;
            }

            if (c == '\\'' || c == '"' || c == '`') { quote = c; continue; }'''

new = '''    private static (int Braces, int Parens, int Brackets) CountDelimiters(string js)
    {
        int braces = 0, parens = 0, brackets = 0;
        char quote = '\\0';

        for (var i = 0; i < js.Length; i++)
        {
            var c = js[i];

            if (quote != '\\0')
            {
                if (c == '\\\\') { i++; continue; }
                if (c == quote) quote = '\\0';
                continue;
            }

            // R164: comments are skipped before quoting, because an apostrophe in prose ("browser's own
            // accessor") opened a string that never closed and swallowed the rest of the body. A guard that
            // miscounts is worse than no guard: it fails a correct body.
            if (c == '/' && i + 1 < js.Length && js[i + 1] == '/')
            {
                while (i < js.Length && js[i] != '\\n') i++;
                continue;
            }

            if (c == '/' && i + 1 < js.Length && js[i + 1] == '*')
            {
                i += 2;
                while (i + 1 < js.Length && !(js[i] == '*' && js[i + 1] == '/')) i++;
                i++;
                continue;
            }

            if (c == '\\'' || c == '"' || c == '`') { quote = c; continue; }'''

if old not in t:
    raise SystemExit("counter anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the guard skips comments before quoting")
