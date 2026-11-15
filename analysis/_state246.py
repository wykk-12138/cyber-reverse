import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 246 轮（新增 `BindingGapRatchetTests` 缺口棘轮：real ≤ 34 且表不可删；2 条通过）。

---

## 缺口现在是**有止回阀**的（R246）

`BindingGapRatchetTests` 在 C# 里独立重算缺口（不复用 python 工具）：

- 读 `docs/xaml_bindings.json`（174 类型 / 819 成员）→ 对 `src/**/*.cs` 全文做词边界匹配；
- 缺失项按**形状**分类：`^(HasMultiple|Value)_\\d+$` 是噪音，其余是真缺口；
- 断言 **real ≤ 34**，失败信息写明"某个改名把已关掉的成员又打开了"；
- 另有一条断言表仍是完整清单，**防止通过删表来减小缺口**。

**为什么单写一份**：python 工具是探索工具（可变），测试是棘轮（必须独立稳定）。两者不一致本身就是信号。

**纪律**：关掉成员时**同一次提交里把 `MaxRealGap` 一起降下来**，永不提高。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
