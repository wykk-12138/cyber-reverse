import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 捡到原版**自己的会话 payload 样本**（第 152 轮）

上一轮留下的 `orientation` 疑问，这一轮在池子里搜的时候撞到一份**完整样本** —— 原版发出去的
那份 JSON。这是本会话第一次拿到它的**遥测 schema**，而不是从类名推。

### 一、样本头（逐字）

```
{"sid":"9a10c34d-…","tid":"3bd808ffef1b18c5…",
 "_t":"ASaMBHzL7WoRfLL6ekqt4MuLNpqk5pjkxXylexg…",
 "cf_flags":"1006579","fresh-cookie":"true","cookie-_cc":"ASaMBHzL7WoRfLL6ekqt4MuL",
 "time-unix-epoch-ms":1778830875801,"time-local":"15-5-2026, 09:41:15",
 "time-string":"Fri May 15 2026 09:41:15 GMT+0200 (Midden-Europese zomertijd)",
 "time-tz-offset-minutes":-120,"time-tz-has-dst":"true","time-tz-dst-active":"true",
 "time-tz-std-offset":-120,"time-tz-fixed-locale-string":"6-3-2014, 07:58:39",
 "dom-local-tag":"ASaMBHzL7WoRfLL6ekqt4MuL","dom-session-tag":"ASaMBHzL7WoRfLL6ekqt4MuL", …}
```

### 二、四处值得命名的地方

| 键 | 说明 |
|---|---|
| `cookie-_cc` | 是 `_t` 的**前 24 个字符** —— cookie 是 token 的截断，**不是独立值** |
| `time-tz-*` 四件套 | 把夏令时写成**状态机**（offset / hasDst / dstActive / stdOffset），而不是一个数字 |
| `time-string` | 带浏览器自己的时区名 —— **`Midden-Europese zomertijd`（荷兰语）**。UA 怎么改都改不掉，因为它来自宿主机 |
| `time-tz-fixed-locale-string` | 把一个**固定瞬间**（2014-03-06 07:58:39）按宿主 locale 格式化 —— 交叉校验「声称的时区 vs 真实时区」最便宜的办法 |

> `-120` 是 JS `getTimezoneOffset()` 的语义（**落后 UTC 多少分钟**），CEST 是 +02:00，所以是 -120。
> 样本的 locale 名写着 `zomertijd`，两半互相作证。

### 三、顺带解决上一轮的疑问

同一份样本里有：

```
"window.screen.orientation.type":"landscape-primary","window.screen.orientation.angle":"0"
```

—— **原版自己报的就是 landscape**（Windows UA）。所以 R151 说的「已知不自洽」不是 replica 引入的，
**那就是原版的常态**。`orientation` 保持原生 = 1:1。

### 四、payload 的指纹部分

`navigator.userAgentData.brands`、connection 四件套（`effectiveType` / `rtt` / `saveData` / `downlink`）、
五个插件（**全部 `internal-pdf-viewer`** + 同一句 `Portable Document Format`）、
`canvas-print-100-999` 与 `-detailed-` 两个哈希、`canvas_spoofing: 0`、`js-errors` 数组、逐字体探测。

还有两个**不是 DOM 属性**的键：

```
"navigator.automationEnabled":false      ← 原版自己写的
"webdriver_detect":false                 ← 原版自己算的
```

**原版把「自己的判断」和「读到的值」放在同一个 namespace 里** —— 检测方无法从命名上区分它们。

### 五、已落成 `SessionPayload`

十六个头键（保序）、`CookieTagLength = 24`、`FixedLocaleDate`、`GetTimezoneOffsetMinutes`、
`IsDaylightActive`、`CookieTagFor`、`CfFlags`、`ComputedKeys`（四个「判断类」键）、
`PluginNames` + 单一 filename/desc、`DarkModeKey/Sample`、`ConnectionKeys`。七条测试。

### 六、这一轮的一句话

> 前一版我在**猜**它发什么；这一轮我看见了它发的东西。
>
> **一份真实样本，胜过十次「从类名推断字段名」。**
'''

if "## 捡到原版**自己的会话 payload 样本**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("payload documented")
else:
    print("already present")
