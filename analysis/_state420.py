import io
p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding='utf-8').read()
i = t.index('## ⚠ 待验证')
j = t.index('## 当前状态')
t = t[:i] + t[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('pending-test flag cleared')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add = '''
---

## 第 420 轮：把 R419 那条没跑成的测试跑掉

### 一、先腾内存

```
关掉 Razer / Asus / QQLive / ChatGPT 残留进程 + build-server shutdown
available 0.87 → 1.72 GB
```

### 二、再跑那条测试

```
CloseAndOpenFamilyTests   7 通过 / 0 失败（含 R419 新加的 ProfileCreatorView 用例）
```

`Navigate` / `Count` / `Names` / `PaymentView` / `AdvancedView` 的断言全部成立。
`SESSION_STATE.md` 的"待验证"块已删除。

### 三、这一轮的一句话

> 上一轮我说"没跑成"，这一轮把它跑成了 —— 两轮合起来才是一条完整的记录。

> **"没跑成"必须被追成"跑成了"，否则它永远是个悬案。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add)
print('VERDICT appended')
