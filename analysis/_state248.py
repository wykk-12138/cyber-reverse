import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 248 轮（五个"类型存在只差一个成员"全部关掉；棘轮 33 → 28；21 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 28`

## 推进方法（R248 的有效切法）

**不要按"缺哪些名字"推进，要按"哪些类型复刻件里本来就有"推进。**

```
python - <<'EOF'   # 见 analysis/_gap_types.py
按 类型是否存在 分组 → 存在的那些，每个通常只差 1 个成员，一轮能做完五个
EOF
```

**已关**（本轮）：`GroupSummary.PinGroup`（读写 `TaskGroup.Pinned`）、`TaskGroupView.Draft`、
`ProxyGroupView.Draft`、`StaggerStartView.TotalTasks`、`NotificationOptions.EnableSound`（`Sound` 的**别名**，不建第二字段）。

**剩余 real 28**：类型不存在的结构差异（`FilterRow`/`Platform`/`ComboBoxEdit`/`ActionConfig`/`LocalizeFormatExtension`/
`Store.ColorSupport`/`AuthWindow`/`LicenseControl`/`User.IsStaff`/`InputRow`/`ActionRow`/`FilterInputEntry`/
`ElementCell.ColumnSpan`/`IWebhook.ExtraFields`/`CreateInputModel.Minus`/`SettingsView.Transition`/
`AycdInboxAccount.TaskCount`/`NotificationSound.SoundLocation`/`BrowserProfile.DisplayName`/`AccountStoreEntry.IsSelected`/
`StoreGroupModal.RemoveStore`）—— 要做需先抽控件或扩模型。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
