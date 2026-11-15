import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 275 轮（`Flow.Source` 落地 + `StoreFlowSourceTests` 守门：literal 与 endpoint 不再混算）。

---

## `StoreFlowSteps.Flow` 现在带来源

```csharp
public enum FlowSource { Literal = 0, Endpoint = 1 }
public sealed record Flow(string Store, IReadOnlyList<Step> Steps,
                          FlowSource Source = FlowSource.Endpoint)
```

- **默认 `Endpoint`**（更弱的一类）—— 漏标只会低估，不会高估；
- `structure-token-multi` / `structure-token-single` 标 `Literal`；
- `StoreFlowSourceTests`（3 条）盯住：Literal 只能那两条、其余必须 Endpoint、说明注释不能被删。

**验证**：Stores 编译 0 错误；Flow 相关 95 条通过；新测试 3 条通过。

## 待做（下次动代码时）

1. 给其余 6 条流补上更精确的来源（有的是"端点 + 部分字面量"，目前一律 `Endpoint` 是保守值）；
2. 用 `docs/flow_step_sequences.json` + `docs/row_groups_wide.json` 给 `structure-token-*` 之外再找出可标的 `Literal` 流。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套；此后为子集）
缺口 33（real = ceiling）    不可达 UI 类 29
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
