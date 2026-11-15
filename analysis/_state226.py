import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 226 轮（"缺失成员"分三类；ProxyView 六个绑定名补成真命令；whole-source 缺口 115→107；1419 绿）。

---

## XAML 绑定表怎么读（R225-R226）

`docs/xaml_bindings.json`（174 类型 / 819 成员）+ `docs/XAML_BINDINGS.md` + `tools/bind_diff.py`。

**引用数字必须带口径**：

- `--per-file`（同名类文件内）：167 缺 —— 会**高估**，因为复刻件常把行为写在别的类
- 默认 whole-source（整个 src/）：**107 缺**，其中泛型噪音 8 个（`HasMultiple_NN`）应扣除

三类缺口的处理方式：

| 类别 | 例子 | 怎么办 |
|---|---|---|
| 真缺行为 | `TaskView.CopyUrl / EditAll / ForceStartSelected / OpenSolvers / OpenStaggerStart` | 找证据再实现 |
| 只在别处 | `UtilitiesView` 四个 StoreGroup（已内联）、`ProxyView` 六个（R226 已提成命名命令） | 需要时提成命名命令 |
| 噪音 | `Models.EditValue\\`1` 的 `HasMultiple_87…101` | 不计入 |

**已完成的命名命令**（按钮真的调用它们）：`ProxyView.AddProxies / ClearAll / CopyProxies / CloneProxies /
DeleteProxies / TestProxies`。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
