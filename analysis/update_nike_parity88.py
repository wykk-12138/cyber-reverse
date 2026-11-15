import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\NIKE_PARITY.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 13. 七个 Nike 标识（第 88 轮，IDA 读出）

```
find_regex "nike-[a-z-]+"   →  4 条；再把两个大写拼法手工确认
```

| 名字 | 地址 | 类型 |
|---|---|---|
| `NIKE-GS` | 0x146df584c | cookie |
| `NIKE-SESSION` | 0x146df5874 | cookie |
| `Nike-Kasada-Version` | 0x146dfbbd4 | header |
| `nike-api-caller-id` | 0x1470e4b84 | header |
| `x-nike-ux-id` | 0x14716b6d4 | header |
| `x-nike-visitid` | 0x14716b704 | header |
| `x-nike-visitorid` | 0x14716b73c | header |

**第 11 节写的「4 个 Nike header 未设置」其实是 7 个标识：4 个 header + 1 个 Kasada 版本 header
+ 2 个 cookie。而 replica 一个都没发。**

已固化为 `Cybersole.Stores.Flows.NikeHeaders`：

- 五个 header 名 → session var 键的映射（`nike.apiCallerId` / `nike.uxId` / `nike.visitId` /
  `nike.visitorId` / `nike.kasadaVersion`）
- `Apply(vars, headers)` 只在**真的观测到值**时才设置该 header，返回设置了几条

`NikeFlow.GetSessionAsync` 现在会把已知的那些塞进 `c.Session.Headers`。

### 为什么不用默认值

一个填了假值的 header 告诉 Kasada「这个客户端在说谎」，比「这个客户端没发这个 header」更糟。
**所以宁可少发，不发假。** `NikeHeaderTests.OnlyKnownValuesReachTheHeaders` 钉住这条。
'''

if "## 13. 七个 Nike 标识" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("NIKE_PARITY section 13 appended")
else:
    print("already present")
