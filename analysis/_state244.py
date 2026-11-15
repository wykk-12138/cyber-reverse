import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 244 轮（新增 `UnassignedFieldGuardTests` 死字段守卫，立刻抓到 R240 的两个死命令；1430 绿）。

---

## 新守卫：`UnassignedFieldGuardTests`（R244）

**规则**：私有字段若**无初始值**且**全文件内没有任何写入**（`=` / `+=` / `ref` / `out` / `++` / `--` / `??=`），判为死字段。

**为什么需要**：字段未赋值时方法第一句 `if (_x is null) return;` 永远命中 —— 编译过、测试过、点了没反应。
编译器看不见，行为测试覆盖不到"没人按的按钮"。

**第一次运行的结果**：抓到 `ProviderViews.cs` 的 `_services`（`RefreshProviders` 恒返回）与 `_dataServices`（从未使用），
**都是 R240 我自己写的**。已修：前者在构造函数赋值并调用一次，后者删除。

**写这条守卫时的教训**：第一版只认 `_field =`，报了 17 个假阳性 —— 因为可观察属性把赋值藏在
`SetProperty(ref _field, value)` 里。**规则要按语言的写入形状写，不是按我想到的那种写法写。**

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
