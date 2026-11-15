import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\NIKE_PARITY.md"
t = io.open(p, encoding="utf-8").read()

# Section 12 (round 87) and the older country note both say twenty-two; the table has forty-two.
t = t.replace("### 22 个支持的国家（第 50 轮）", "### 支持的国家：**42 个**（第 89 轮更正；第 50 轮只读到 22 个）")

old = """**第 11 节写的「4 个 Nike header 未设置」其实是 7 个标识：4 个 header + 1 个 Kasada 版本 header
+ 2 个 cookie。而 replica 一个都没发。**"""
new = """**第 11 节写的「4 个 Nike header 未设置」其实是 7 个标识：4 个 header + 1 个 Kasada 版本 header
+ 2 个 cookie。而 replica 一个都没发。**

## 13b. 国家表是 42 个，不是 22 个（第 89 轮更正）

第 50 / 86 轮记的是 22 个市场，于是 `NikeFlow.Countries` 只有 22 项，`CountryFor("UK")` 还
因为「二进制没有 GB 市场」而回落到 US。第 89 轮直接查：

```
find_regex "Nike [A-Z]{2}$"   →  42 条（0x28 字节间隔，按字母序）
```

```
AT AU BE BG CA CH CZ DE DK ES FI FR GB GR GS HR HU IE IL IN IT JP
LU MX MY NL NO NZ PH PL PT RO SE SG SI SK TH TR TW US VN ZA
```

**`GB` 就在里面。** 之前那 22 个是这张表从 `IT` 开始的一段——**读到的是窗口，不是表**。

所以 R86 引入了一个真实的错：把 UK 的请求打到美国去。现在：
`Countries` 42 项、按字母序、`UK → GB`、`DE → DE`、`FR → FR`，只有表外的（`CN` 等）才回落到 US。"""

if old in t and "13b." not in t:
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("NIKE_PARITY corrected to 42")
else:
    print("anchor missing or already corrected")
