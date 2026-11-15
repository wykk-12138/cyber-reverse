import io

p = r"D:\projects\cyber-reverse\replica\tools\endpoint-provenance.py"
t = io.open(p, encoding="utf-8").read()

old = '''def consts_in(body, start, end):
    """Consts declared directly in a scope (text between start and end)."""
    text = body[start:end]
    plain = dict(PLAIN.findall(text))
    return plain, ASSEMBLED.findall(text)'''

new = '''def consts_in(body, start, end, nested):
    """Consts declared *directly* in a scope.

    <para>
    R128: a scope's text contains its nested classes' text, and several classes here declare their
    own <c>Base</c>. Reading the range as one blob collapsed those constants last-wins and resolved
    John Lewis's paths against Scheels' base. The nested ranges are blanked out first.
    </para>
    """
    text = list(body[start:end])
    for n_start, n_end in nested:
        if n_start > start and n_end < end:
            for i in range(n_start - start, n_end - start + 1):
                if 0 <= i < len(text):
                    text[i] = " "
    text = "".join(text)
    plain = dict(PLAIN.findall(text))
    return plain, ASSEMBLED.findall(text)'''

if old not in t:
    raise SystemExit("consts_in anchor missing")
t = t.replace(old, new, 1)

old_call = '''            plain, assembled = consts_in(body, start, end)'''
new_call = '''            nested = [(o_start, o_end) for _, o_start, o_end, _, _ in
                      [(n, s, e, None, None) for n, s, e in scopes(body)]]
            plain, assembled = consts_in(body, start, end, nested)'''
if old_call not in t:
    raise SystemExit("call anchor missing")
t = t.replace(old_call, new_call, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("nested scopes are blanked before reading a scope's consts")
