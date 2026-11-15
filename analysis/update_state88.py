import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 87 轮。", "最后更新：第 88 轮。"),
    ("**891 通过 / 0 失败 / 2 跳过**", "**895 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R87）。", "上一次跑：全 PASS（R88）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **IDA 关掉之后的重开流程（R87 实测）**"
add = '''- **Nike 14 步的子路径：当前证据不可达，别再试。** R88 三条路都走到头：
  ① 20 个 URL 是连续存放的一张表，邻域没有 `/shipping_address` 之类碎片；
  ② `find_regex "(shipping_address|/shipping|…)"` 命中的全是别的店；
  ③ **修复后的 IDA 库里函数名全是 `sub_140xxxxxx`**（`func_query name_regex` 返回空），
  `NIKE_PARITY` 里那 14 个名字来自**字符串**里的 `d__N` 状态机名，不是符号。
  → 除非拿到运行期抓包，这一层没有更多可挖的。
- **Nike 的标识是 7 个不是 4 个。** `find_regex "nike-[a-z-]+"` + 两个大写拼法：
  4 个 header（`nike-api-caller-id` / `x-nike-ux-id` / `x-nike-visitid` / `x-nike-visitorid`）
  ＋ `Nike-Kasada-Version` ＋ 2 个 cookie（`NIKE-SESSION` / `NIKE-GS`）。
  已固化为 `NikeHeaders`，`GetSessionAsync` 按 session var **只发已知值**（不编默认值）。
- **IDA 关掉之后的重开流程（R87 实测）**'''
if anchor in t and "Nike 14 步的子路径" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
