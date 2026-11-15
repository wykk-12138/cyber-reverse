import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 255 轮（Profile.Delivery / Settings.MonitorConcurrency / InputModal+DropdownModal 四个；缺口 57）。

---

## 棘轮当前值：`MaxRealGap = 57`

## 编辑方法上的硬教训（R252 已犯一次、R255 又犯两次）

用正则插代码时我把"锚点行 + 新增"拼在 `m.end()`，**锚点行被写两遍** → `CS0102`。
**规则**：插入前明确锚点行要保留几次（0 或 1）；更稳的做法是**用替换**（把锚点行替换成"锚点行 + 新增"），
而不是在 `m.end()` 处拼接。

## `ProfileProxyBindingTests` 的作用

它维护一份"`Profile` 里声明了但没人引用的字段"清单。本轮 `Delivery` 落进清单 →
**必须记进已知集合**，这等于强制承认"还没接线"，而不是假装完成。

## 剩余 57 的头部

`Attributes.Platform` 3（不可得）/ `ProfileCsvRow` 3 / `FilterRow` 3 / `CreateInputModel` 2 /
`Store` 2 / `ComboBoxEdit` 2 / `ProfileCsvEditorView` 2 / `CaptchaProvidersView` 2 /
`GoogleAccountEditView` 2 / `PayPalAccountCreatorView` 2 / `SettingsView` 2 / `ActionRow` 2 /
`SmartActionsCreator` 2（DeleteParam/UseTemplate）… 其余各 1。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
