import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 230 轮（SmartActionsCreator 补 8 个；剩下 5 个卡在模型上而非名字上；缺口 83；1425 绿）。

---

## 缺口 96 → 83，剩余分两类

```
R225 167(per-file 高估) → R226 107 → R227 105 → R228 105 → R229 96 → R230 83
```

**A. 只缺名字/入口**（可快速推进）：`UtilitiesView` 4、`TaskCreatorMainView` 4、`Platform` 3 …

**B. 卡在模型**（要先扩模型 + 序列化测试，写进 `docs/XAML_BINDINGS.md`）：
- `SmartAction.Actions`（多动作）+ `ActionParams` / `ActionConfig` → `AddAction` / `DeleteAction`
- `SmartActionFilter.Inputs` + `FilterInputEntry` → `AddInput` / `DeleteInput` / `DeleteParam`
- `SmartActionFilter.Behaviour`（AND/OR）→ `ToggleFilterBehaviour`

**C. 噪音**：`Models.EditValue\\`1` 的 `HasMultiple_NN` 12 个，**不计**。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
