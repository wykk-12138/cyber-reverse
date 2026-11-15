import io
p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding='utf-8').read()
i = t.index('## ⚠ 未验证的改动')
j = t.index('## 当前状态')
t = t[:i] + t[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('unverified flag cleared')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add = '''
---

## 第 417 轮：把上一轮"未验证"的那两条验证掉

### 一、内存处置后再验

```
关掉 ChatGPT（266 MB + 若干子进程）→ available 1.96 → 2.40 GB
dotnet build -m:1（单进程，少吃内存）→ exit 0
copy 测试（TaskCreator / ProfileCsv / PageCopy / AccountCopy）→ 50 通过 / 0 失败
```

**R416 那两条 delete-confirm 字符串的转义没问题。**

### 二、同时把状态文件里的警示块删掉

`SESSION_STATE.md` 顶部的"⚠ 未验证的改动"整段移除 —— 它已经完成使命。
**留着比删掉更糟**：下一轮会以为还有未验证的东西。

### 三、这一轮的一句话

> 上一轮我写"未验证"，这一轮我把它变成"已验证"，并把警示撤掉。

> **"未验证"是一个待办项，不是免责声明。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add)
print('VERDICT appended')
