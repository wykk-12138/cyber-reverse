"""R1296: the coverage generator still counted rows in a file R1282 deleted.

`wiring_row_count()` opened src/Cybersole.Stores/Scripts/VendorWiring.cs and counted `new Row(` occurrences. R1282 removed
that file because the table had no real caller, so the function now returns None and the document says the table was
removed rather than reporting a count of nothing. This is the generator being fixed, not the generated file.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tools/core_coverage.py'
text = io.open(P, encoding='utf-8').read()

old_fn = '''def wiring_row_count():
    w = os.path.join(ROOT, "src", "Cybersole.Stores", "Scripts", "VendorWiring.cs")
    text = io.open(w, encoding="utf-8", errors="replace").read()
    return text.count("new Row(")
'''

new_fn = '''def wiring_row_count():
    """Rows in the vendor wiring table, or None once that table is gone.

    R1282 removed src/Cybersole.Stores/Scripts/VendorWiring.cs: nothing in the running product called it, and the vendor
    evidence it carried lives in docs/VENDOR_WIRING.md. Counting `new Row(` in a file that no longer exists is not a
    measurement, so this returns None and the report states the removal instead of a number.
    """
    w = os.path.join(ROOT, "src", "Cybersole.Stores", "Scripts", "VendorWiring.cs")
    if not os.path.exists(w):
        return None
    text = io.open(w, encoding="utf-8", errors="replace").read()
    return text.count("new Row(")
'''

if old_fn not in text:
    raise SystemExit('function anchor missing')
text = text.replace(old_fn, new_fn)

# the rendering line: make it None-safe
old_line = ('    add("%d 行 × 9 列（`Vendor` · `Marker` · `Cookie` · `State` · `Note` · `MarkerFrom` · `Gap` · `Solver` · '
            '`Relayed`）。" % wiring_n)')
new_line = ('    if wiring_n is None:\n'
            '        add("接线表已于 R1282 删除（`VendorWiring.cs` 在运行期无真实调用者，取证与对照移入 "\n'
            '            "`docs/VENDOR_WIRING.md`）—— 这里不再有行数可数。")\n'
            '    else:\n'
            '        add("%d 行 × 9 列（`Vendor` · `Marker` · `Cookie` · `State` · `Note` · `MarkerFrom` · `Gap` · "\n'
            '            "`Solver` · `Relayed`）。" % wiring_n)')
if old_line in text:
    text = text.replace(old_line, new_line)
    print('render line made None-safe')
else:
    print('WARN: render line not matched, check L182')

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('generator updated')
