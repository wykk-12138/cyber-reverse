import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 224 轮（测量结果收成 `docs/GUI_GEOMETRY.md` 权威表 + `GeometryLedgerTests` 守卫；1414 绿）。

---

## 测量纪律（R217-R224 的总结论）

**尺寸只有两种身份：测过的，或估的。** 以后改任何尺寸：

1. 先看 `docs/GUI_GEOMETRY.md`（唯一权威表）；
2. 新量一个数字 = **两个样本**（窗口矩形枚举，或两个窗口宽度下的像素测量），单样本不算结论；
3. 三处同时改：表、代码常量（旁边写方法）、`GeometryLedgerTests`；
4. **量不出来的（最后一列/像素内容）必须标注"量不出来"，不许估一个数**。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
