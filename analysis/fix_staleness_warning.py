"""R1297: METRICS called a current artifact stale because it read the mtime count and not the content count.

artifact_freshness.py has separated the two since R1183: `source files newer than the artifact` counts mtimes, and
`of those, changed against HEAD` says how many of those files actually differ. A mutation run rewrites every target and
restores it, so it bumps mtimes and leaves content identical — which is exactly what happened here (17 newer, 0 changed,
`publish artifact state: current`). The warning now fires only when something really changed.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tools/metrics_report.py'
text = io.open(P, encoding='utf-8').read()

old = '''            if low == "source files newer than the artifact" and str(value).strip() not in ("0", ""):
                warnings.append(
                    "**函数数量那一行来自一个陈旧的 `.publish-aot`**：有 %s 个源文件比产物新（共 %s 行）。"
                    "它描述的是更旧的一次构建，不是当前源码。"
                    % (value, _bit("产物陈旧度（.publish-aot vs src）", "lines in those files")))'''

new = '''            if low == "source files newer than the artifact" and str(value).strip() not in ("0", ""):
                # R1297: newer is mtime, changed is content, and only the second one means the artifact is behind.
                # A mutation run rewrites each target and restores it, so it leaves files newer but byte-identical;
                # warning about that would be a false alarm every single round.
                changed = _bit("产物陈旧度（.publish-aot vs src）", "of those, changed against HEAD")
                if str(changed).strip() not in ("0", ""):
                    warnings.append(
                        "**函数数量那一行来自一个陈旧的 `.publish-aot`**：有 %s 个源文件比产物新，其中 %s 个相对 HEAD 真的改过（共 %s 行）。"
                        "它描述的不是当前源码。"
                        % (value, changed,
                           _bit("产物陈旧度（.publish-aot vs src）", "lines in those files")))'''

if old not in text:
    raise SystemExit('warning anchor missing')
io.open(P, 'w', encoding='utf-8', newline='\n').write(text.replace(old, new))
print('staleness warning now keyed on content, not mtime')
