import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 383 轮：把实机落盘的字段名**钉进测试**（43 + 10 + 4 + 7 个名字）

### 一、`solvers.json` 直接证实了 R361 的推断

```json
[ { "solvers": [ { "name": …, "view": …, "reload": …, "settings": {
      "autoBoundingBox", "autoTickBox", "autoCanvas", "questionSharing",
      "autoClick", "reCaptchaSegmentation", "reCaptchaMultiClassification" } } ] } ]
```

- `Solver` 的 `name` / `view` / `reload` / `settings` —— **正是 R361 从绑定表补上的四个**；
- `SolverSettings` 的 7 个字段 —— 与复刻件**逐个相同**。

### 二、新测试 `LiveSchemaPinsTests`（3 个用例）

把三份实机 JSON 的字段名作为字面量数组写进测试：

| 用例 | 字段数 |
|---|---|
| `TheSettingsFileFieldsAllExist` | 43 |
| `TheTaskGroupFileFieldsAllExist` | 10 |
| `TheSolverFileFieldsAllExist` | 4 + 7 |

任何一个属性被改名，这三个用例就会红 —— **比文档里的表格可靠。**

### 三、又栽在大小写上

第一版 43 个里报 33 个"缺" —— 我把属性名转成小写，却没把 JSON 的 camelCase 名也转，
`quickTaskProfiles` 对不上 `quicktaskprofiles`。两边都折叠后全绿。

```
完整套件   1541 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 我这一轮做的不是"补功能"，而是**把外部证据变成回归约束**。

> **证据看过就忘；写成断言才会一直说话。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 383 轮（`LiveSchemaPinsTests`：把实机 JSON 的 43+10+4+7 个字段名钉进测试）。

---

## 现在的"最硬约束"三件套

| 约束 | 内容 |
|---|---|
| `LiveSchemaPinsTests` | 实机落盘的字段名（settings / taskGroup / solver / solverSettings） |
| `bind_scope.py` | 类型级绑定缺口 12 |
| `bind_diff.py` | 名字级缺口 17 |

**改名字会同时被第一和第三条抓到。**

## 状态

```
完整套件   1541 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
