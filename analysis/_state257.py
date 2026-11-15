import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 257 轮（GoogleAccountEditView 2 + PayPalAccountCreatorView 2；缺口 48；一次编译通过、守卫全绿）。

---

## 棘轮当前值：`MaxRealGap = 48`

## 三个动作，对应前几轮踩过的三个坑（R257 已验证有效）

| 坑 | 动作 |
|---|---|
| 锚点行写两遍（R252/R255） | **一律用替换**（`replace(anchor, anchor + 新增)`），不在 `m.end()` 拼接 |
| 字段没赋值（R243/R244/R253） | 构造时取初值；`private set` 的属性用**受控写入方法**（`SetEditMode`），不放宽成 public |
| ceiling 猜错（R254/R255） | **先测后设**，ceiling 只等于实测值 |

**结果**：一次编译通过、死字段守卫没响、101 条受影响测试全绿。

## 剩余 48 的头部

`Attributes.Platform` 3（不可得）/ `ProfileCsvRow` 3 / `FilterRow` 3 / `CreateInputModel` 2（Minus/Plus）/
`Store` 2 / `ComboBoxEdit` 2 / `ActionRow` 2 / `SmartActionsCreator` 2（DeleteParam/UseTemplate）/
`SettingsView` 2 … 其余各 1。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
