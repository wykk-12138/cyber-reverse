import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R337：头像面板（`• My License`）—— 复刻件原来是另一个窗口

实机点右上头像（**不记录账号名与邮箱**，只记结构）：

```
•  My License
      (avatar)
      <display name>
      <email>
   [ Dashboard ↗ ]
──────────────────────────────
Terms of Service  •  Privacy Policy            [ Log Out ]
```

复刻件原来是 `Account` 窗口：`Session` 卡片里 `Email / Subject / Role / Expires` 四行 + `Open dashboard` / `Sign in` / `Log out` 三个平按钮。

### 按实机重写

| 项 | 实机 | 复刻件现在 |
|---|---|---|
| 顶栏 | `•  My License` | 同（`\\u2022  My License`） |
| 头像 | 圆形 | `Border` 圆角 32 + 字形占位 |
| 名字 / 邮箱 | 两行（名字大、邮箱小且淡） | 同（名字取邮箱 @ 前段，占位 `(signed out)`） |
| 主按钮 | `Dashboard ↗`，整行宽 | 同 |
| 页脚 | `Terms of Service • Privacy Policy` 左、红色 `Log Out` 右 | 同 |
| `Subject/Role/Expires` 三行 | **没有** | **删掉** |

### 两处诚实标注

1. `TermsUrl` / `PrivacyUrl` 两个地址**没有出处**（实机只给了按钮，没给链接目标）→ 标 `inferred: no image evidence (R337)`；
2. **`Sign in` 改成"无会话时才显示"** —— 实机是已登录态，面板上没有它；
   但 R213 的理由（没有会话时要有一条登录入口）仍然成立，所以留着、只隐藏。

### 教训

删掉 `Sign in` 后，`LoginControl` 立刻变成"声明但从未构造"，四条测试变红 —— 
**守卫逼我把"删"改成"条件显示"。** 这是守卫第二次挡住我的过度删减（第一次是 R300 的 `ADVANCED` 页面）。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 337 轮：头像面板 —— 复刻件原来根本不是这个窗口

### 一、实机结构

```
•  My License / (avatar) / name / email / [ Dashboard ↗ ]
──────────────────────────────────
Terms of Service  •  Privacy Policy            [ Log Out ]
```

（**不记录账号名与邮箱**，只记结构。）

复刻件原来是 `Account` 窗口：`Session` 卡片 `Email/Subject/Role/Expires` 四行 + 三个平按钮。

### 二、重写要点

顶栏 `•  My License`、圆头像、名字+邮箱两行、整行宽 `Dashboard ↗`、页脚
`Terms of Service • Privacy Policy` + 红色 `Log Out`；**删掉 `Subject/Role/Expires` 三行**。

### 三、两处诚实标注

- `TermsUrl` / `PrivacyUrl` **无出处** → 标 `inferred: no image evidence (R337)`；
- **`Sign in` 改为"无会话时才显示"** —— 实机是已登录态、面板上没有它；
  但 R213 的理由（无会话要有登录入口）仍成立，所以留控件、只隐藏。

### 四、守卫又一次救了我

删掉 `Sign in` 后，`LoginControl` 立刻变成"声明但从未构造"，**四条测试变红**
（`UnreachedUiTypesTests`、`SummaryBlockTests`、`ItHasAnEntryPointInTheAccountWindow`、
`TheLoginIsHostedAtTheMeasuredFrameAndTitle`）→ 逼我把"删"改成"条件显示"。

> 这是守卫第二次挡住我的过度删减（第一次是 R300 的 `ADVANCED` 页面）。

### 五、验证

```
完整套件   1490 通过 / 0 失败 / 2 跳过
新增       ProfilePanelTests（2 条）
```
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
