import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            if (c == '\\\\' && js[i + 1] is 'n' or 't')
            {
                var name = "\\\\" + js[i + 1];
                if (!found.Contains(name)) found.Add(name);
                i++;
            }
        }

        return found;
    }'''

new = '''            if (c == '\\\\' && js[i + 1] is 'n' or 't')
            {
                var name = "\\\\" + js[i + 1];
                if (!found.Contains(name)) found.Add(name);
                i++;
            }
        }

        return found;
    }

    /// <summary>
    /// True when the <c>/</c> at <paramref name="index"/> starts a regular expression rather than a division: the
    /// character before it, ignoring spaces, is one of the tokens a regex can follow (R172).
    /// </summary>
    private static bool StartsRegex(string js, int index)
    {
        for (var i = index - 1; i >= 0; i--)
        {
            var c = js[i];
            if (char.IsWhiteSpace(c)) continue;
            return c is '=' or '(' or ',' or ':' or '[' or '!' or '&' or '|' or '?' or '{' or '}'
                or ';' or '>' or '+';
        }

        return false;
    }'''

if old not in t:
    raise SystemExit("escape scanner tail anchor missing")
t = t.replace(old, new, 1)

# the delimiter counter must skip regex literals as well
old2 = '''            if (c == '\\'' || c == '"' || c == '`') { quote = c; continue; }

            switch (c)'''

new2 = '''            if (c == '\\'' || c == '"' || c == '`') { quote = c; continue; }

            // R172: a regex literal's brackets are not code — `[^(]` and `\\(\\)` are one character class and one
            // escaped pair, and counting them made a correct body look unbalanced.
            if (c == '/' && StartsRegex(js, i))
            {
                i++;
                while (i < js.Length && js[i] != '/')
                {
                    if (js[i] == '\\\\') i++;
                    i++;
                }
                continue;
            }

            switch (c)'''

if old2 not in t:
    raise SystemExit("delimiter switch anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the guard understands regex literals")
