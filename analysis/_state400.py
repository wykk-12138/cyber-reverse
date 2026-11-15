import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 400 轮：把上一轮"改不动"的那处改掉了（先动结构，再动文案）

### 一、结构改动

`EmptyView` 原本只有 `Bodies` 词典 + `For(page)`，而 `UiKit.Empty(Headline)` 是单行版本。
新增 `EmptyView.Body(key)`（取不到就空串），并给词典补了两个键：

```
"cloudflare"   = "Add a Cloudflare provider to get started"      ← Settings.CloudflareSolvers.EmptySubtitle
"smartActions" = "Add a smart action to get started"
```

### 二、文案改动

```csharp
var empty = EmptyView.For("cloudflare");   // 原来是 UiKit.Empty(EmptyView.Headline)
```

现在这个页面说的是**自己的话**，不再借用代理页那句。

### 三、守卫的处置

`EmptyViewTests.EveryPageUsesTheSharedControl` 原来断言 `UiKit.Empty(EmptyView.Headline)` 出现在该文件里 ——
**行为没变（仍然用共享控件、共享标题），只是入口换成了 `For(page)`**，所以改守卫而不是改代码。

### 四、验证

```
EmptyViewTests（含新用例 EachPageCanCarryItsOwnSecondLine）
完整套件   1575 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 上一轮我说"这要动结构，先记着"；这一轮把结构动了，文案跟着就改成了。

> **"以后再说"只有在"以后真的做了"的时候才成立。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 400 轮（`EmptyView.Body(key)` + Cloudflare 页改用自己的空状态文案；套件 1575）。

---

## `EmptyView` 现在支持"每页一句话"

```csharp
EmptyView.Body("cloudflare")   // "Add a Cloudflare provider to get started"
EmptyView.For("cloudflare")    // 完整控件
```

词典键：checkouts / feed / tasks / accounts / proxies / profiles / **cloudflare** / **smartActions**

## 状态

```
完整套件   1575 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
文案       4 区清零；Settings 21 条近似错误待核对（1 条已解决：Cloudflare 空状态）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
