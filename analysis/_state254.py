import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 254 轮（AccountGrid 2 + AnalyticsView.ChangeChart；缺口 63；`OpenRelease` 因缺数据源撤掉）。

---

## 棘轮当前值：`MaxRealGap = 63`

## 纪律补充（R254）

1. **ceiling 只能等于测出来的数**，不能等于"我以为会关掉几个"（本轮先设 61、实测 63）。
2. **命令要先有数据源**：`AnalyticsView.OpenRelease` 编译期就露了三处缺口
   （`AnalyticsDocument` 无 `Releases`、`AppServices` 无 `Browser`、方法叫 `LoadAnalytics` 不是 `Reload`），
   前两个是"复刻件里没有这个能力"，所以撤掉而不是造一个空壳。

## 已知不可做（勿重复尝试）

| 名字 | 缺什么 |
|---|---|
| `Attributes.Platform` 三值 | 值不在池子里；下拉点不开 |
| `AnalyticsView.OpenRelease` | 无 release 目录、无浏览器服务 |
| `FilterRow` / `ProfileCsvRow` / `ActionRow` / `ComboBoxEdit` | 行/控件不存在（内联构造） |
| `LocalizeFormatExtension.Value2` / `LocalizeSwitchExtension.Condition` | 无本地化扩展类型 |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
