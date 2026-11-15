import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\IDB_EVIDENCE.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 5.18.32 的新库：能做什么、不能做什么（第 95 轮）

数据库重建完成（`auto_analysis_ready: true`，约 14 分钟），`find_regex` 恢复正常。
但**两条「定位代码」的路都被证明走不通**，这是确定结论，不要再试：

| 想做的事 | 结果 | 原因 |
|---|---|---|
| `xrefs_to <字符串地址>` | `xref_count: 0` | NativeAOT 不产生数据交叉引用，字符串通过偏移表间接访问 |
| `find type=immediate/imm/refs/ref/data` 找绝对地址 | `count: 0`（全部类型） | 同上：代码用 RIP 相对寻址，绝对地址不是立即数 |
| `insn_query` 找引用该地址的 `lea` | `scanned: 200000, count: 0` | ① 需要整数操作数；② 默认只扫 20 万条指令（全 `.text` 是 200 万级） |

> **结论：在这份镜像上，「哪个函数引用了这条字符串」无法用 IDA 查出来。**
> 能做的是「这条字符串存在/不存在」（`find_regex`）和「函数级反编译给定地址」（`decompile`），
> 前者已经用了 5 轮，后者缺一个入口地址 —— 而入口地址只能从前者来，闭环断在这里。

### 本轮真正拿到的东西：Demandware 的完整 URL 模板

```
find_regex "Sites-[A-Za-z0-9_]+-Site"  limit 12  →  5 条
```

```
https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/
https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct
https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Product-Variation?pid=
https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit
on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-Config
```

四条独立事实：

1. **路径形状确认**：`/on/demandware.store/Sites-{site}-Site/{locale}/{controller}` —— replica 的
   `Controller()` 一直是对的（这条是难得的「猜对了」）。
2. **locale 不是常量**：Marc Jacobs 用 `default`，Stone Island 用 `en_US`。
3. **两个新控制器**：`SaleRegistration-SignupSubmit`、`SaleRegistration-Config` —— 抽签/发售登记链。
4. **站点 id ↔ 域名**：`cpcompany→cpcompany.com`、`mjsfra→marcjacobs.com`、`StoneNA→stoneisland.com`。
   只有这三对是**同一字面量里成对出现**的；`asics/crocs/vans` 只出现站点 id，**不猜域名**。

已固化为 `DemandwareControllers` 的 `Hosts` / `SitePath()` / `SiteRoot()`，
`DemandwareControllerTests.TheSitePathReproducesTheImagesUrls` 逐字比对三条 URL。
'''

if "## 5.18.32 的新库" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("IDB_EVIDENCE: R95 section appended")
else:
    print("already present")
