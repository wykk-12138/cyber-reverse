import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 从 schema 到会发出去的 payload（第 153 轮）

上一轮记下样本，这一轮让它能被真正构建出来：`SessionPayloadBuilder.Build(Inputs)`。

### 一、三条「自洽规则」被写进代码

| 规则 | 代码形态 |
|---|---|
| `cookie-_cc` 是 `_t` 的前 24 字符 | `SessionPayload.CookieTagFor(token)`；`Inputs` **没有**这个字段，想传错都传不进来 |
| 时间四件套描述**同一个瞬间** | 都从 `Now` 派生 |
| 固定瞬间不是「现在」 | `time-tz-fixed-locale-string` 用 `SessionPayload.FixedLocaleDate` |

### 二、一个实测抓到的错

第一次跑测试：

```
Expected: "15-5-2026, 09:41:15"
Actual:   "15-5-2026, 07:41:15"
```

`1778830875801` 是 **07:41:15 UTC**，而样本写 **09:41:15** —— 差两小时，正好是 `getTimezoneOffset() == -120`。
所以 `time-local` 必须是**同一瞬间按声称时区偏移后**再格式化：

```csharp
["time-local"] = inputs.Now
    .ToOffset(TimeSpan.FromMinutes(-inputs.TimezoneOffsetMinutes))
    .ToString("d-M-yyyy, HH:mm:ss", CultureInfo.InvariantCulture),
```

**如果两个键各自取值，payload 就会自相矛盾地讲两个时间。** 这条是测试逼出来的，不是我先想到的。

### 三、固定格式与「可注入格式」

`FixedLocalePattern = "d-M-yyyy, HH:mm:ss"` —— 样本的 `6-3-2014, 07:58:39` 正是这个模式
（日不补零、月不补零、逗号、补零时钟）。**用的是模式而不是 culture 查表**：
样本那台机器的 culture 不保证这台机器装了，而模式本身就是证据。
调用方仍可传 `FixedLocaleString` 覆盖。

### 四、七条测试

键序 == `SessionPayload.HeadKeys`、cookie tag 三处同源且 `Inputs` 无可传字段、
时间四件套同瞬间且固定串≠当前串、布尔是字符串形态（关闭时给 `"false"` 而非缺键）、
固定模式复现样本、可注入格式、**构建器不读时钟**（同输入同字节、以 `{"sid":` 开头）。

### 五、这一轮的一句话

> 上一轮我说「一份真实样本胜过十次推断」。这一轮它立刻兑现了 —— 样本里的 `09:41:15`
> 直接指出我算错了时区偏移。
>
> **样本最值钱的地方，是它能反驳你；一份只会被赞成的资料，等于没有。**
'''

if "## 从 schema 到会发出去的 payload" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("builder documented")
else:
    print("already present")
