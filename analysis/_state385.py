import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 385 轮：我的"修复"其实没生效 —— 属性用错了序列化器

### 一、上一轮的修正是假的

R384 我给 `BackupDocument` 加了 `[System.Text.Json.Serialization.JsonPropertyName("proxies")]`。

**这个项目用的是 Newtonsoft.Json**（`AppPaths.Json.Default`：`CamelCaseNamingStrategy` + 自定义转换器）。
STJ 的属性 Newtonsoft 完全不看 —— 于是文件里写出来的仍然是 `proxyGroups` / `taskGroups` / `billingGroups`。

**更糟的是：我上一轮加的测试读的正是 STJ 属性，所以它通过了。**

### 二、改对

1. 属性换成 `[Newtonsoft.Json.JsonProperty("proxies")]` 等九个；
2. 测试改成**真的序列化一次**：

```csharp
var json = JsonConvert.SerializeObject(new BackupDocument(), Json.Default);
var written = JObject.Parse(json).Properties().Select(p => p.Name);
Assert.Equal(live.OrderBy(x => x), written.OrderBy(x => x));
```

```
完整套件   1542 通过 / 0 失败 / 2 跳过
```

### 三、这一轮最值得记的一条

> **一个测试如果断言的是"注解"，它就保护不了"行为"。**

我上一轮的测试绿灯，而文件格式仍然是错的 —— 这是"测试通过 + 功能错误"的最坏组合。
现在的测试会真的写一遍 JSON，再读它的键。

### 四、顺带确认

项目用 camelCase 策略，所以 `AccountsDocument` 的 `AccountGroups/PayPal/Imap/AycdInbox`
自动序列化成 `accountGroups/payPal/imap/aycdInbox` —— 与实机 `accounts.json` 完全一致，不需要额外注解。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §14 断言"注解"的测试保护不了"行为"（R385）

R384 我给备份文档加了 `System.Text.Json` 的 `JsonPropertyName`，而这个项目用 **Newtonsoft**，
属性完全被忽略 —— 文件照旧写错键名。而我当时写的测试**读的是注解本身**，于是绿灯。

规则：

1. 断言序列化结果，就**真的序列化一次再读键**（`JsonConvert.SerializeObject` + `JObject.Parse`）；
2. 加特性前先确认这个项目用的是哪个序列化器（`grep -r PropertyNamingPolicy|CamelCaseNamingStrategy`）；
3. 绿灯不等于正确：**测试要落在"用户能看到的东西"上**（文件内容、界面文本、返回值），不要落在中间表示上。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §14 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 385 轮（**R384 的修复没生效**：属性用错序列化器；已改 Newtonsoft 并让测试真的序列化）。

---

## 序列化器（务必记住）

```
项目用 Newtonsoft.Json
AppPaths/Store.Json.Default = CamelCaseNamingStrategy + StringEnum(camelCase) + TimeSpanJsonConverter
Formatting.Indented, NullValueHandling.Ignore, DateTimeZoneHandling.Utc
```

**`System.Text.Json` 的属性在这个项目里是死的。** 要改键名只能 `[Newtonsoft.Json.JsonProperty]`。

## 状态

```
完整套件   1542 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
文件格式   settings / tasks / solvers / checkoutHistory / .cyb 五项已对齐并钉住
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
