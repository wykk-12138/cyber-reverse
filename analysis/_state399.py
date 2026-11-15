import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 399 轮：又一次"改了又撤回"，但这次记下了**为什么改不动**

### 一、目标：Cloudflare 页的空状态

复刻件的 Cloudflare 页显示的是**代理页那句话**（"Add some proxies to get started"），
而原版这句是 `Settings.CloudflareSolvers.EmptySubtitle` = `Add a Cloudflare provider to get started`。
**这处差异没有歧义**（页面上根本不放代理）。

### 二、三次尝试，三次被挡

1. `UiKit.Empty(EmptyView.Headline, "…")` → **`Empty` 只有一个参数**（我以为是两个）；
2. 改成 `UiKit.Empty("…")` → 守卫 `EmptyViewTests.EveryPageUsesTheSharedControl` 红了：
   它要求这些页面**必须**读 `EmptyView.Headline`；
3. 结论：要改这句，得先给 `EmptyView` 增加"每页副标题"的能力，并同步那个守卫。

**这是结构改动，不是文案改动** —— 已在本轮留档，不半途而废。

### 三、记下来比硬改更重要

`replica/src/.../ProviderViews.cs` 的那行注释现在写着：这句为什么还不对、正确文案是什么、被谁挡着、下一步该做什么。

```
完整套件   1574 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 我第三次在同一类事情上停手 —— 前两次是"看不清位置"，这次是"看清了位置但改法要动结构"。

> **知道"为什么现在不能改"，和知道"该怎么改"一样值钱。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 399 轮（Cloudflare 页空状态：想改但被 `EmptyView` 结构挡住，已留档在代码注释里）。

---

## 待做：`EmptyView` 需要"每页副标题"

- 现状：`UiKit.Empty(EmptyView.Headline)` 单行；守卫 `EmptyViewTests.EveryPageUsesTheSharedControl` 强制使用它
- 需要：`EmptyView` 支持每页副标题（如 `EmptyView.For(key)` 带 subtitle）
- 受益页：Cloudflare（`Add a Cloudflare provider to get started`）等

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
文案       4 区清零；Settings 21 条近似错误待核对；Cloudflare 空状态待结构改动
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
