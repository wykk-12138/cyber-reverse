"""R1307 round record + roadmap pointer for the async tail map."""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
ROADMAP = 'docs/REMAINING_REPLICATION_ROADMAP.md'

ROUND = """
---

## 第 1307 轮：把「77 条支付长尾」从一句没出处的数字，做成一张三态表

- **问题**：路线图写着「支付异步名 124 个、已覆盖 47、剩 77」，店铺侧「103 个、剩 33」，但**没有名单**。
  任何一个想做长尾的会话都得先信这个数字。
- **做法**：镜像仍保留 `<名字>d__NN` 状态机串（`analysis/ida_strings.txt` 里有 801 个不同名字、1291 次出现），
  拿它跟 `replica/src` 逐个比。新增 `analysis/async_tail.py`，产物 `docs/ASYNC_TAIL.md`。
- **三次修正，每次都把一个假数字变成真数字**（这是本轮真正的价值）：
  1. 只比裸标识符 → 报 **801 里 723 缺**。那不是覆盖率，那是命名习惯：镜像里 `Login` 的状态机叫
     `<Login>d__25`，复刻件写的是 `LoginAsync`。
  2. 允许 `Async` 后缀不同 → 仍有 `ContinueUnzerThreeDs` 被判缺席，而它在 `Gateways.cs` 的**文档注释里点了名**，
     行为由 `RunUnzerThreeDsAsync` 承担。于是判定从两态改成三态：
     **declared**（有同名方法）/ **mentioned**（源码出现过但不是声明）/ **absent**（根本没有这个串）。
     **只有 absent 才是覆盖缺口。**
  3. `ProcessThreeDs` 仍是 absent——复刻件写的是 `Process3DSAsync`（数字 3 而非 Three）。
     补上数字↔英文两种拼法后，declared 219 / mentioned 97 / **absent 485**；支付家族 110 个名里 **absent 66**。
- **所以「剩 77」现在的可信读法是**：支付家族 110 个镜像名中，66 个在复刻件源码里**一次都没出现过**，
  44 个是换名实现或仅文档点名。66 里还混着被关键词误分类的项（`TokenizeText`、`DetectByteOrderMarkAsync`、
  `RefreshTokenAsync` 等 MSAL/浏览器项），真属于支付的还要再筛一遍。
- **下一轮的路已经探明**：状态机名字是**按类编号**的，且同一处元数据里成串出现。例如 `0x14338377d` 那一串是
  `<GetStripeConfiguration>d__87`、`<SetStripePayment>d__88`、`<CreateStripePaymentMethod>d__89`、
  `<SubmitStripeOrder>d__90`、`<HandleRequiresAction>d__91` … `<CreateUnzerResource>d__99`、
  `<SubmitUnzerOrder>d__100`、`<GetUnzerCallback>d__107`；`0x143384b28` 甚至是一张
  `SquareCardType` / `BuildFingerprints` / `GetStripeConfiguration` 的方法名表。
  **这说明同一个店铺类的支付方法可以按序枚举**——比逐个猜名字高效得多。

### 五要素

- **改了什么**：新增 `analysis/async_tail.py`（三态判定 + 数字/英文拼法归一 + `--write-doc`）、
  新增生成物 `docs/ASYNC_TAIL.md`（150 行）。**没有改 `replica/src` 与 `replica/tests`**，
  因此不重发布 AOT、不重跑变异（R1306 的绿仍描述当前树）。
- **验证命令与输出**：`python analysis/async_tail.py` → 801 名 / declared 219 / mentioned 97 / absent 485；
  `python analysis/async_tail.py --family payment` → 110 / absent 66；
  `dotnet test --filter "DocsConsistency|ParityDoc|DocumentNumbersAreSourced|HandoffHeadPointer|SourceEncoding|ClaimsCoverage"`
  → **24/24 通过**（新文档没有破坏任何文档守卫）。
- **数字变化**：本轮的产出是**分类**而非度量；`docs/METRICS.md` 不需要重生成（树未变，产物仍 `current`）。
- **证据等级**：Observation —— 801 个状态机名及出现次数、三态各自的判定与名单、`0x14338377d` 那串按类编号的名字。
  Inference —— mentioned 一档多数是换名实现（抽样验证了 4 个：`ContinueUnzerThreeDs`、`CardinalInit`、
  `CardinalContinue`、`GetUnzerCallback` 都在源码里但非声明）。Unknown —— 66 个 absent 里各自对应镜像哪个函数
  （名字 → 地址 → 函数这条链本轮**没有**做）。
- **还剩什么**：把 66 个 absent 逐个定位到函数并落地；店铺家族 34 个 absent；`other` 385 个（多数是框架项，需再筛）。
"""

ROADMAP_ADD = """
  5. **长尾名单已落成表**（R1307）：`docs/ASYNC_TAIL.md` 是生成的，把镜像 801 个 `<名字>d__NN` 状态机名
     按 declared / mentioned / absent 三态对上复刻件源码。**支付家族 110 个名里 66 个 absent**，
     店铺家族 74 个里 34 个 absent。**取件优先从这张表的 absent 列里挑**，不要再用「剩 77」这个没有出处的数字。
     定位方法已探明：状态机名按类编号且成串出现（如 `0x14338377d` 是
     `<GetStripeConfiguration>d__87` … `<SubmitUnzerOrder>d__100` 一张序列表），可据此按类枚举方法。
"""

POINTER = """
---

## 第 1307 轮

- 长尾有了名单：`docs/ASYNC_TAIL.md`（由 `analysis/async_tail.py --write-doc` 生成），三态
  declared / mentioned / absent，**只有 absent 算覆盖缺口**。支付家族 110 名里 absent 66，店铺 74 里 34。
- 三次修正过程写在 `replica/docs/VERDICT.md`：裸名比对→允许 Async→三态→数字/英文拼法。
  前两版分别报出 723 和 80，都是**命名差异冒充缺口**。
- 本轮未改 `replica/src`，AOT 未重发布、变异未重跑（R1306 的绿仍描述当前树）。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1307 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1307 \u8f6e')

# The roadmap gains a fifth item under the static-work section.
text = io.open(ROADMAP, encoding='utf-8').read()
anchor = '  4. **`Topps`**'
if 'ASYNC_TAIL' in text:
    print('roadmap already points at the tail map')
elif anchor in text:
    # insert after item 4's block: find the end of that bullet (next blank line after it)
    start = text.index(anchor)
    end = text.index('\n\n', start)
    text = text[:end + 2] + ROADMAP_ADD + text[end + 2:]
    io.open(ROADMAP, 'w', encoding='utf-8', newline='').write(text)
    print('roadmap updated with the tail-map item')
else:
    print('roadmap anchor not found; skipped')
