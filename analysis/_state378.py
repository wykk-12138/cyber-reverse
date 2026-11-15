import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 378 轮：`CloudflareSolversView.FetchBalance`（缺口保持 14，成员级减少）

### 一、把 lambda 提成成员

原来"Fetch balance"按钮里是一整段内联逻辑（找第一个 provider → 没 key 就抱怨 → 向驱动要余额 → 保存 → 刷新）。
现在：

```csharp
public string FetchBalance()   // 返回页面要显示的那一行
```

按钮变成两行：`status.Text = FetchBalance(); Refresh();`

### 二、两条早退被测试钉住

```
没有 provider       → "No Cloudflare provider configured."
有 provider 无 key  → "cf: no API key, so no balance to ask for."
```

这两条是"不该发请求"的分支 —— 以前只能靠点按钮才能到达。

### 三、验证

```
ProviderFetchBalanceTests   2 通过
完整套件                    1538 通过 / 0 失败 / 2 跳过
bind_scope                  14（还差 Edit）
```

### 四、这一轮的一句话

> 提取一个成员的价值不在"名字对上"，而在**把原本只能靠点击触发的分支变成可断言的**。

> **能测试的分支，才是真的分支。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 378 轮（`CloudflareSolversView.FetchBalance` 提取；套件 1538 通过）。

---

## 提取成员的收益（这一轮的例子）

`FetchBalance()` 把按钮里的整段逻辑变成可调用成员，于是**两条"不该发请求"的早退分支**第一次有了测试：

```
没有 provider      → "No Cloudflare provider configured."
有 provider 无 key → "cf: no API key, so no balance to ask for."
```

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 14（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
