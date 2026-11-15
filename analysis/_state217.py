import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## ⚠️ 欠着两件事')
head = '''最后更新：第 217 轮（把原版的窗口矩形全量出来了：Splash 529x630 / Monitor·Solver·Login 都是 1536x814；复刻件四个尺寸原先全是估值）。

---

## 原版窗口清单（R217 实测，改 GUI 前先看这张表）

```
vis=True   1429x892  'Cybersole'   主壳（可缩放）
vis=False  1536x814  'Monitor'     启动即建、隐藏
vis=False  1536x814  'Solver'      启动即建、隐藏
vis=False  1536x814  'Login'       启动即建、隐藏
启动瞬间    529x630  'Cybersole'   启动画面（标题与主壳相同）
```

复刻件已按此改：`SplashWindow` 529x630、`MonitorWindow`/`SolverWindow` 1536x814、
登录宿主标题 `Login` 尺寸 1536x814。守卫：`WindowGeometryTests`。

**未实现的 1:1 细节（故意留着，等你决定）**：原版启动就把 Monitor/Solver 建成隐藏窗口，复刻件是点按钮才建。
照做要付常驻内存，所以只记录。

---

'''.replace('\\\\', '\\')
out = lf[:i] + head + lf[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
