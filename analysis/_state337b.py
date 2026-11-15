import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 337 轮（头像面板按实机重写：`• My License` / 头像 / 名字邮箱 / `Dashboard ↗` / 页脚两链接 + 红色 `Log Out`）。

---

## 实机核对第八个面：头像面板

复刻件原来是另一个窗口（`Account` + `Email/Subject/Role/Expires` 四行 + 三平按钮）。
现按实机改为：`•  My License` → 圆头像 → 名字 → 邮箱 → 整行宽 `Dashboard ↗` → 分隔线 →
`Terms of Service • Privacy Policy` 左 + 红色 `Log Out` 右。

- `TermsUrl` / `PrivacyUrl` **无出处**，标 `inferred: no image evidence (R337)`；
- `Sign in` 改成**无会话时才显示**（实机已登录态没有它，但 R213 的理由仍成立）。

**守卫再次挡住过度删减**：删掉 `Sign in` 后 `LoginControl` 变成未构造，四条测试变红 → 改成条件显示。

## 状态

```
完整套件   1490 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
账号信息   实机面板上可见，**未记入任何文档**
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
