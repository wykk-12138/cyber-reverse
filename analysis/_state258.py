import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 258 轮（不编译不测试：把 48 个缺口收成 `docs/BINDING_BACKLOG.md` + `tools/backlog_report.py`）。

---

## ⚠ 内存：8.15 GB（硬线 8 GB 附近）

本轮**故意不编译、不跑测试**。下轮如果还要动代码，建议先重启（`dotnet build-server shutdown` 只能回收约 1 GB）。

## 缺口账本（唯一入口）

`docs/BINDING_BACKLOG.md` —— 48 = **A 类 15（类已在，只差成员）** + **B 类 33（类不存在，结构差异）**。

重算：`<python> tools/backlog_report.py`（口径与 `BindingGapRatchetTests` 一致：剥注释 + 排除噪音）。

A 类里 **2 个不可得**：`AnalyticsView.OpenRelease`、`Attributes.Platform` 三值。
B 类里 **5 个行控件不存在**（`FilterRow`/`ProfileCsvRow`/`ActionRow`/`InputRow`/`FilterInputEntry`）、
**3 个本地化扩展不存在**（`LocalizeSwitchExtension`/`LocalizeFormatExtension`）。

## 工具坑（Windows）

`Set-Content -Encoding UTF8` 会写 **BOM** → Python 报 `U+FEFF`。按字节删 `\\xef\\xbb\\xbf` 解决。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
