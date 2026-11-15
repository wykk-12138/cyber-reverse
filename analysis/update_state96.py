import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 95 轮。", "最后更新：第 96 轮。"),
    ("**912 通过 / 0 失败 / 2 跳过**", "**916 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R95）。", "上一次跑：全 PASS（R96）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **「字符串存在性」查得到"
add = """- **PDB 这条路断了（R96）**：`Temp\\ida\\Cybersole.pdb\\…\\Cybersole.$$$` 是 0 字节占位；
  更新包 `Cybersole-5.18.32-win-x64-full.nupkg`（57 MB / 11 条目）**不含任何 .pdb**。
  `sub_*` 换不了真名，别再找。
- **Shopify 只有两个购物车端点：`cart/add.js`、`cart/update.js`。**
  `cart/change.js`、`cart/clear.js` 在镜像里**不存在**（Shopify 文档里有，但这个二进制不调）。
  R96 已把 `ShopifyFlow` / `StoreFlow` 三处改掉，`ShopifyCartEndpointTests` 禁止它们回来。
- **镜像里有 1,182 个 `*.myshopify.com` 主机**，已逐字导出 `docs/shopify_hosts.txt`
  （进了 `verify.ps1` 文档检查 + `ShopifyHostListTests` 钉住数量/唯一/字母序/形态）。
- **换工具不如换问题（R96）**：「谁引用了这条字符串」问不出来；「这个平台用了哪几个端点」
  一次 `pe_strings` dump 就全有，而且立刻查出四个假货。
- **「字符串存在性」查得到"""
if anchor in t and "PDB 这条路断了" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
