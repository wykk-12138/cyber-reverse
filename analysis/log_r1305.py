"""R1305 round record for VERDICT.md and HANDOFF.md (UTF-8, append-only)."""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1305 轮：Topps 那条 Unknown 问错了地址；类形从反射元数据读出来了

- **先纠错**：`off_1449B8EB0` 是**一个 JSON 类型句柄**（`names_at` 三格全是类型描述符，不是字符串），
  所以「在 `off_1449B8EB0` 的精确序列化 JSON 键名」这个问法，那个地址从来没能力回答。
  它唯一的引用点是 `sub_140C9E420` 里的 `sub_142E65500(v4, &off_1449B8EB0, v5)`——一次反序列化调用。
- **镜像仍保留反射元数据**，因此类形是可读的：`0x143351CB7…0x14335221C` 一串
  `get_X` / `Create_X` / `XPropInit` 三元组 + `_X` 存储字段名，解出类型 `ToppsCommerceProduct` 的七个属性：
  `PriceAmount`、`ProductImage`、`ProductVariant`、`SelectedOption`、`VariantImage`、
  `ToppsCommerceProductUrl`、`JToken`；旁边还有四个列表承载名 `ListProductImage` / `ListProductVariant` /
  `ListSelectedOption` / `ListToppsCommerceProduct`——**说明载荷是集合而不是扁平对象**。
- **仍 Unknown 的只剩一处**：序列化键的**大小写**。元数据里名字带尾缀 `@`，name→handle 是哈希键，
  所以 `^PriceAmount$` 与 `^priceAmount$` 两种拼法在字符串库里都是 0 命中——按可达性铁律，0 命中不构成缺席证明。
  于是读取器**按大小写不敏感匹配**，而不是选一种拼法去赌。
- **落码**：`ToppsCdn`（`PropertyNames` / `ListPropertyNames` / `Parse`）+ `FindProductCdnAsync` 接回：
  载荷是裸数组或包在四个承载名任一之下都能读；`topps.schema` 从写死 `"unknown"` 变成**记录识别到的形状**
  （`ToppsCommerceProduct`），并落 `topps.count` / `topps.products` / `topps.productUrl`。
  非 JSON / HTML 拦截页 / 意外形状一律返回空列表而不是抛异常——CDN 返回 404 正文是正常答案。
- **测试里最有意思的是那三条 `[Theory]`**：同一个产品用 PascalCase 与 camelCase 写，读进同样的字段；
  承载名 `ListToppsCommerceProduct` 三种大小写都能找到。**这就是那条 Unknown 换来的行为**，
  而不是测试的巧合。

### 五要素

- **改了什么**：新增 `replica/src/Cybersole.Stores/Flows/ToppsCdn.cs` 与
  `replica/tests/Cybersole.Tests/ToppsCdnTests.cs`（13 条，含 Theory 展开）；`ShopifyFlow.cs`
  （接回解析 + 改写 Unknown）；三处文档口径纠正；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter ToppsCdnTests` → **13/13**；
  `dotnet test --filter "Shopify|Topps"` → 见本轮记录；`artifact_freshness.py` → `state: current`；
  `metrics_report.py` → 全部 exit 0；`mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**（均引 `docs/METRICS.md`）：套件 `2530/0/0` → 见 METRICS 当前值（+13）；
  产物 `61,227,008` → **`61,246,976`** 字节。
- **证据等级**：Observation —— 七个属性名与四个承载名及其地址、`sub_142E65500` 的反序列化调用点、
  两种拼法在字符串库都 0 命中。Inference —— 载荷是这些对象的集合（由四个 `List*` 承载名推出）。
  Unknown —— 序列化键的大小写。
- **还剩什么**：Unzer `qword_1472c65a0+8` 终态集与 `0x14094a870` 谓词；ACS 各处理器方法体；
  Komoju 两个请求体的目标 URL；33 条店铺长尾 + 77 条支付长尾。
"""

POINTER = """
---

## 第 1305 轮

- Topps 那条 Unknown 是问错了对象：`off_1449B8EB0` 是 JSON 类型句柄，不是键名表。类形已从镜像的反射元数据
  读出（`ToppsCommerceProduct` 七个属性 + 四个 `List*` 承载名），落成 `ToppsCdn` 并接回 `FindProductCdnAsync`。
- **仍 Unknown** 只剩序列化键的大小写；读取器按大小写不敏感匹配绕开，两种拼法都有测试。
- 见 `replica/docs/VERDICT.md` 第 1305 轮。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1305 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1305 \u8f6e')
