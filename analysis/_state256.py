import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 256 轮（CaptchaProvidersView 2 + ProfileCsvEditorView 2；缺口 52；新增 ProfileCsvParse 纯函数测试）。

---

## 棘轮当前值：`MaxRealGap = 52`

## 待观察的 flake（不要无证据就改）

`GlobalSurfaceTests.NoNameIsAdvertisedWithoutAProperty` 在全套里失败一次，**单独跑连续三次都通过**。
与 R237 的 `ChromeIsGone` 同类（只在满负载失败），但**这次没有抓到"读到旧值"那种证据**，
所以本轮不改测试，只记录。**下次全套再出现就查它。**

## 本轮新增的纯函数与测试

`ProfileCsvEditorView.Parse(csv)` 从 `Apply()` 里提出来，`ProfileCsvParseTests` 3 条覆盖：
表头跳过 / 无表头 / 空白输入。它决定"粘贴多少建多少"，而且不依赖窗口。

## 剩余 52 的头部

`Attributes.Platform` 3（不可得）/ `ProfileCsvRow` 3 / `FilterRow` 3 / `CreateInputModel` 2（Minus/Plus）/
`Store` 2 / `ComboBoxEdit` 2 / `GoogleAccountEditView` 2 / `PayPalAccountCreatorView` 2 / `ActionRow` 2 /
`SmartActionsCreator` 2（DeleteParam/UseTemplate）… 其余各 1。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
