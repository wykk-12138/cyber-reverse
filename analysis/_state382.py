import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 382 轮：拿**实机落盘数据**核对模型（这一轮最硬的证据）

### 一、发现了什么

原版的数据目录是 `%APPDATA%\\Cybersole`，里面是**明文 JSON**：

```
settings.json 4.1 KB   tasks.json 2 KB   solvers.json   billing.json
accounts.json  proxies.json  smartActions.json  checkoutHistory.json
Backups\\*.cyb         BrowserData\\
```

这比 locale、比 GUI 都硬：**这是程序自己写出来的、它认的字段名。**

### 二、新工具 `tools/live_schema_diff.py`

把每个落盘 JSON 的键，与复刻件里对应类的属性名（首字母小写）对差集。

```
settings.json   GlobalSettings   live=43  replica=48  missing=none
tasks.json      TaskGroup        live=10  replica=25  missing=none
billing.json    list[1]: id, name, profiles
accounts.json   dict: accountGroups, payPal, google, imap, aycdInbox
proxies.json    list[1]: id, name, order, behaviour, proxies, totalDownload, totalUpload
smartActions.json dict: actions, templates
```

**两个最关键的模型（设置、任务组）在字段层面完全对上。**

### 三、工具先骗了我一次

第一版报 `tasks.json` 缺 `running` —— 其实 `TaskGroup.Running` 是**表达式体属性**（`public int Running =>`），
我的正则只认 `{ get;`。修好正则后 0 缺失。

**这正是 METHOD §10.1 说过的"工具会撒谎"，这次它撒在"缺失"方向。**

### 四、这一轮的一句话

> 我一直在用 locale 猜字段、用 GUI 猜位置；**程序自己写的 JSON 早就摆在那里两年了。**

> **最硬的证据，往往躺在最不起眼的目录里。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 382 轮（发现实机落盘 JSON，新增 `tools/live_schema_diff.py`；设置/任务组字段全对上）。

---

## 新的最硬证据源：`%APPDATA%\\Cybersole\\*.json`

```
python tools/live_schema_diff.py
```

| 文件 | 类 | 结果 |
|---|---|---|
| `settings.json` | `GlobalSettings` | live 43 / replica 48，**缺 0** |
| `tasks.json` | `TaskGroup` | live 10 / replica 25，**缺 0** |
| `billing.json` / `accounts.json` / `proxies.json` / `smartActions.json` | — | 顶层结构已记录 |

**这是程序自己写的字段名** —— 比 locale 和 GUI 都硬。

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
