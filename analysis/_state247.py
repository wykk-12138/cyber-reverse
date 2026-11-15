import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 247 轮（MonitorWindow.OpenFilter；**第一次把棘轮 34 → 33**；146 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 33`

R246 立的纪律第一次被执行：关掉成员 → **同一次提交里降 ceiling**。
只改代码不改数字 = 白留一格余量 = 棘轮失效的开始。

## 明确"不可做/结构差异"的清单（不要重复尝试）

| 名字 | 为什么 |
|---|---|
| `Attributes.Platform` 的 `InputType/QuantitySupport/QuantityAutoAdjustSupport` | 值不在池子里；下拉点不开（R242 二次复现） |
| `LocalizeFormatExtension.Value2`、`LocalizeSwitchExtension.Condition` | 复刻件无本地化扩展类型 |
| `ComboBoxEdit.ClearSelectionCommand/RemoveTokenCommand` | 复刻件用 `UiKit` 组合，无该控件 |
| `ActionRow.IsFirst`、`FilterInputEntry.IsFirst`、`ActionConfigEntry`、`AccountStoreEntry.IsSelected` | 行控件不存在（内联构造） |

**这些要从"缺口"里读成"结构差异"，除非真的去抽控件。**

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
