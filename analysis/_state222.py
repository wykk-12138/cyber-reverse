import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 欠账状态')
head = '''最后更新：第 222 轮（Home 左右比例 1.87:1、左栏固定 324 px —— 都是两个窗口宽度量出来的；1410 绿）。

---

## 已测出的几何账本（改尺寸前必看）

| 对象 | 实测值 | 方法 |
|---|---|---|
| 主壳 | 1429x892 可缩放 | 枚举窗口矩形 |
| Monitor / Solver / Login | 1536x814，登录标题 `Login` | 同上 |
| 启动画面 | 529x630，居中，寿命 ≥4.35 s，标题 `Cybersole` | 同上 |
| Home 左右栏 | **1.87 : 1**，间隙 24 px | 两个窗口宽度读面板边界 |
| 左栏（Proxies/Billing/Accounts） | **固定 324 px** | 两个窗口宽度读组卡片边界 |
| Tasks 表四列 | Site 1.21 : Product 2.29 : Profile 1.14 : Proxies 1.00 | 两个窗口宽度读表头左边界 |
| Tasks 表 Status 列 | **量不出来**（空表时吸收余量） | 已写进注释与测试 |

'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
