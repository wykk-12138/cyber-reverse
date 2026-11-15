import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 240 轮（CaptchaProvidersView 2 + DataView 3；缺口 55 / real 43；27 条受影响测试绿）。

---

## 缺口 55（real 43）

```
R234 67 → R236 65 → R238 63 → R239 59 → R240 55     noise 12 不计 → real 43
```

**已完成**：TaskView 30/30、ProxyView 6、UtilitiesView 5、MainWindow 7、MonitorWindow 5、
TaskCreatorView 4、SmartActionsCreator 8、AccountGrid 2、PaymentView 2、NotificationsView 2、
SizeCreatorView 3、CaptchaProvidersView 2、DataView 3。

**剩余 real 43 的结构**：
- **卡在模型（12）**：SmartActionsCreator 5（多动作/Inputs/Behaviour）、CreateInputModel 4、Attributes.Platform 3
- **需抽控件（5）**：ComboBoxEdit 2、FilterRow 3
- **零散单成员（~26）**：见 `python tools\\bind_diff.py --buckets`

## 一个反复出现的错误类型（R238-R240 各一次）

"我以为模型长这样"：`PaymentView._services` 不存在、`_disabled` 重名、`Captcha.Configs` 应为 `Captcha.Registry.Configs`。
**都能被编译器抓住**。真正危险的是**编译通过但语义错**的地方 —— 那要靠测试与交叉验证。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
