"""R1296 (cont.): with the wiring table gone, a "missing" list would be thirteen false positives.

The comparison this report exists to make is image inventory against the wiring table. R1282 removed the table, so the
second half simply is not there — reporting every image vendor as missing would be the R764 shape again (a wrong
comparison producing a confident, wrong inventory). The report keeps the image side and says the comparison is
unavailable, and the metric line reports missing=-1 so no reader mistakes it for zero.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tools/vendor_coverage.py'
text = io.open(P, encoding='utf-8').read()

# 1. do not compute a missing list that has nothing to compare against
old = ('    missing = []\n'
       '    for name, pattern, n, addr in found:\n')
new = ('    # R1296: with the table removed there is nothing to compare against, so a missing list would name all\n'
       '    # thirteen vendors -- a confident wrong answer rather than an honest "not applicable".\n'
       '    missing = []\n'
       '    for name, pattern, n, addr in (() if wiring_removed else found):\n')
if old not in text:
    raise SystemExit('missing-loop anchor missing')
text = text.replace(old, new)

# 2. say it in the document instead of leaving the reader to infer it
old_hdr = '    add("**原版清单从二进制取证 ↔ `VendorWiring` 逐条对**。")'
new_hdr = ('    if wiring_removed:\n'
           '        add("**原版清单从二进制取证**；接线表已于 **R1282 删除**（`VendorWiring.cs` 在运行期无真实调用者，"\n'
           '            "取证与对照移入 `docs/VENDOR_WIRING.md`），所以本表**只有镜像侧清点，没有逐条对照**。")\n'
           '    else:\n'
           '        add("**原版清单从二进制取证 ↔ `VendorWiring` 逐条对**。")')
if old_hdr not in text:
    raise SystemExit('header anchor missing')
text = text.replace(old_hdr, new_hdr)

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('vendor_coverage.py now reports the removed table honestly')
