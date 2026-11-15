import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 原版窗口清单')
head = '''最后更新：第 218 轮（Tasks 表列比例从两个窗口宽度解出：1.21 / 2.29 / 1.14 / 1.00；第五列量不出来，已标注）。

---

## 已测出的几何数据（改任何尺寸前先看这里）

| 对象 | 实测值 | 证据方式 |
|---|---|---|
| 主壳 | 1429x892（可缩放） | 枚举窗口矩形 |
| Monitor / Solver / Login | 都是 1536x814，登录标题 `Login` | 同上 |
| 启动画面 | 529x630，标题也是 `Cybersole` | 同上（启动后 300ms 内） |
| Tasks 表四列比例 | Site 1.21 : Product 2.29 : Profile 1.14 : Proxies 1.00 | 两个窗口宽度下读表头左边界 |
| Tasks 表 Status 列 | **量不出来**（空表时最后一列吸收余量） | 已在代码注释与测试里写明 |

**未实现的 1:1 细节（故意留着）**：原版启动即建 Monitor/Solver 隐藏窗口，复刻件点按钮才建 —— 要付常驻内存。

---

'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
