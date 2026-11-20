# 卡点解决方案报告（R702 · 2026-11-16）

> 本轮目标：读 `HANDOFF_BLOCKERS.md` 的路线与六问，把没做完的探测做完，出解决方案。
> **本轮不做实现**——(a) 由裁决结案（范围外），(b) 的规则已取到反编译证据、实现留给下一轮。
> 证据等级逐条标注；所有命令可复算。

---

## 〇、一句话总结

**两条卡点在同一天各自松动**：
(a) `LicenseControl.Authenticate` —— YG 裁决「登录凭证功能，不做」，**范围外结案**；
(b) 剩余 2 条文案 —— 四个维度的**规则全部从反编译里读出来了**（此前一轮都不知道），路径 B 从「猜」变「有据」，同时新方法推翻了 §124「字符串→函数天然为空」的悲观结论。

---

## 一、本轮交付的新方法（两条卡点共用的钥匙）

### 1.1 第三条定位法：冻结字符串 → rip-relative disp32 → 调用点 → 反编译

**§124 的五探针测的是什么**：xref、`.rdata`/`.data` 里的绝对指针、`find_xref_signatures`、`trace_data_flow`——全部是 **IDA 的引用通道**。它们为空是真的。

**但它们漏了什么**：NativeAOT 用 `lea reg, [rip+disp32]` 把冻结字符串对象（`[mt:8][len:4][utf16]`，§35 布局）**按位移**物化进 `.text`。这些 disp32 字节就躺在代码里，裸扫文件即可找到：

```
对 .text 的每个字节位置 p：
  disp = int32(p)；target = VA(p) + 4 + disp；target ∈ 目标集 → 命中
```

**校验**（Observation）：
- 正例：`TEMP`（§35 已证被 `sub_140F39D80` 引用）→ 命中 `0x140F39DE0`，上下文正是 `48 8D 0D`（lea rcx）。
- 负例修正：`Auth.License.Activate` 对齐扫描 0 命中、反编译却引用它（`off_146B53570`，main 第 2303 行）→ lea 的 disp32 可在**非对齐**位置。补 `disp32_scan_any.py`（numpy 全字节滑窗）后命中 `0x14076A803`。
- **教训**（写进工具头）：对齐扫描的 0 命中不能下结论；要下结论必须用非对齐版。

**工具**（全部带「为什么现有不够用」的文件头）：
| 工具 | 干什么 |
|---|---|
| `analysis/disp32_scan.py` | 对齐位 disp32 扫描（快速版） |
| `analysis/disp32_scan_any.py` | **全字节**滑窗（结论级；含 license_csv / license_ctl 两组 preset） |
| `analysis/site_to_func.py` | 命中点 → `.pdata`（277,094 条）二分 → 所在函数 |
| `analysis/names_at.py` | 反编译里任意 `off_/unk_` → 冻结对象解码（字符串/指针表） |

**适用边界**（诚实声明）：只对**独立冻结对象**有效。打包 blob 里的碎片（locale JSON 正文、绑定描述符块、假数据表行）依旧不可达——它们的"名字"不是被 lea 的独立对象。这与 R691 的结论不冲突，是它的补全。

### 1.2 对六问里其余问题的落点

- **Q3（0.581 怎么读）**：建议按尺寸分桶出对照表（§47/48 数据已在），报告口径从单比值改为"大函数趋 1、胶水塌陷"。未做（纯整理工作，留待需要时）。
- **Q4（效率代理）**：三级阶梯方案（同簇函数尺寸 → 冷启动指标 → CUA 脚本化交互计时）已在本轮口头给出，未立项。
- **Q5（C10 三分）**：判别器已想好（关 trimming 诊断构建 / 字符串指纹 disp32 扫产物），未执行。
- **Q6（坑的操作入口）**：本轮自己踩了 AGENTS 红线第 2 条的近亲（pe_strings 是文件偏移不是 VA，连错两次靠正例校准）——印证「清单没覆盖 AGENTS 规则层」，建议 `trap_entry_inventory.py` 补扫一遍。

---

## 二、卡点一 (a)：`LicenseControl.Authenticate` —— 范围外结案

### 2.1 裁决

> YG（2026-11-16）：「LicenseControl是登陆凭证功能吗，本项目主要用于复刻cybersole的功能，
> 登陆凭证功能只是用来管理用户的不需要做，这点可以写进项目记忆」

落地物：`docs/DECISION_LICENSE_OUT_OF_SCOPE.md`（裁决原文 + 适用范围 + 证据副产品归属）。

### 2.2 已实施

1. `analysis/type_presence_triage.py`：新增 `NOT_IN_FUNCTION_SET = {"AuthWindow", "LicenseControl"}`，
   判定优先于文本打分 → 输出 `NOT_IN_FUNCTION_SET=2, RENAMED=7, STRUCTURAL=1, UNKNOWN…=7`，17 条计数不变。
2. 复算：`metrics_report.py --skip-tests` 四项度量与基线一致（4/0/17/80）；
   `TypePresenceTriageTests` + `OriginalViewClassParityTests` **6/6 通过**。
3. 本轮早些时候一度实现过 `LicenseControl.cs`（走完编译+度量），**已按裁决完整回滚**——
   工作树里 replica/ 与度量文档回到基线（git checkout，快照目录已删）。
   保留的分析产物：`license_control_main.c`（2387 行）、`license_refs_resolved.txt`、`license_chain.json`。

### 2.3 对 (a) 判定的净效果

| 之前（R700） | 现在 |
|---|---|
| 17 条 = 7 RENAMED + 1 STRUCTURAL + **1 UNIMPLEMENTED** + 8 UNKNOWN | 17 条 = 7 RENAMED + 1 STRUCTURAL + **2 NOT_IN_FUNCTION_SET** + 7 UNKNOWN（AuthWindow 从 UNKNOWN 并入范围外） |

**UNIMPLEMENTED = 0。** (a) 的文字判据「类型缺失 → 0（不可得则写明）」现在满足：
每条都有判定与依据；唯二的范围外条目依据是**裁决本身**（最高级别的 authority）。
剩余 7 条 UNKNOWN 全部在 R683/R685 写明「缺什么」（词太泛 / 6·35 同分候选），
其中 `LoginControl` 一族同属登录功能，后续若要把 UNKNOWN 收干净可援引同一裁决。

---

## 三、卡点二 (b)：剩余 2 条文案 —— 规则已解出，路径 B 有据可依

### 3.1 定位链（全部 Observation，命令可复算）

```
裸键 ProfileCsv.Error.UnknownCountry  obj VA 0x146E4D160（pe_strings 0x06e4bd6c，mt=chars-12）
裸键 ProfileCsv.Error.UnknownState    obj VA 0x146E4D1B8
python analysis/disp32_scan_any.py --all license_csv
  → UnknownCountry 命中 0x140F7739E；UnknownState 命中 0x140F7784E
python analysis/site_to_func.py …
  → Country 发出函数 sub_140F77350（141 B）；State 发出函数 sub_140F777E0（158 B）
```

### 3.2 逐维度证据（此前四个维度全 Unknown，现在全有反编译依据）

**维度①：何时校验 —— 构建列定义时注册，每行求值。**
`sub_140F74A40`（318 行，落盘 `csv_validator_host.c`）按列构建验证器：` First Name`/` Last Name`/` Address 1`/…/` Country`/` State`/` Barangay`（列名是 **Concat(资源名, 本地化后缀)**，`sub_141CF6230` = string.Concat）。
` Country` 列挂两个单例缓存守卫（`sub_142FB1EBC`→`sub_140F77320`，`sub_142FB1EC8`→`sub_140F77350`），
` State` 列挂 `sub_142FB1FF4`（同族）。**即：校验发生在 CSV 编辑器的行校验里，每行每列求值**——不是导入时一次性。

**维度②：归一化 —— Trim()，仅此。**
守卫公共前段 `sub_140F752D0`：装箱值 → `sub_141CFA390`（= **string.Trim()**：`sub_141CFA500` 用分类表 `byte_144AEBF28`，负类集合实测 = `\t \n \v \f \r 空格`）→ 查表。**没有 ToLower**。

**维度③：大小写 —— 查表本身大小写不敏感（查表函数内置 ignore-case 回退），不依赖调用方传参。**
`sub_142E74840`（列表 Contains）→ 比较链 `sub_141DC16E0 → sub_141DC17A0(mt, ptr, len, 0, 0) → sub_141DC1950`：
先试精确序数比较（`a2==a1` 引用相等 / 逐字符 ordinal），失败后若被查对象的 MethodTable 带 0x40000 位
（大小写折叠表存在），**自动以 `options|1`（ignore-case）重试**（`sub_141DC1950` 尾部 `a4 | 1u`），
折叠比较在 `sub_141DC39A0`（字符级 case-folding switch）。
**结论：`"united states"` 能过，`" UNITED STATES "` 也能过（Trim+ignorecase），`"U.S."` 不能过（无缩写展开）。**

**维度④：按国家还是按 locale —— 两层。**
- Country 守卫：在**单例 `qword_1472C7440` 的双表**里查（先 `[+8]` 后 `[+0]` 回退）——即 R677/R688 量过的**按语言分份的 country 表**。
- State 守卫（`sub_140F777E0`）：**先查 Country 行，取 `[行+96]` 的州表**；**州表为空或长度 ≤0 → 静默放行**（不报错）。
  即"州名单挂在国家行上"——**按国家取州**，与 R669 从中文文案 `{1} 中未知的州/省"{0}"` 推的语义一致，现在有了代码依据。
- 出错文案：Country 一参格式化（`sub_141CF6EA0`，StringBuilder.Format）；State 两参（`sub_141CF6BF0` → `sub_142D3D750(fmt, args, 2)`，
  第二参是 `[选中Country行+72]`——**所在国家名**），对应 `{0}=州值 {1}=国家名`。

### 3.3 处置建议（仍需 YG 点头，但性质变了）

R689 的四路径里，**D（拿规则）已达成**。因此：

- **路径 B（实现校验）不再是猜**：规则四维全有据——`Validate()` 对 Country 列 = Trim 后在当前 locale 的 country 表 Contains（ignore-case）；对 State 列 = 先定位国家行，行无州表则放行，有则州表 Contains；未命中分别发两条既有文案。**建议采纳 B**。
- 路径 A（改口径）不再必要——判据 (b) 原文的「剩余仅池中截断」前提仍假，但 B 能让这 2 条**有发出路径**，从而走到「不可得」之外的另一条满足方式（文案在复刻件里可达）。
- 风险声明：实现时须注明「规则依据 = R702 反编译链」，并保留 `Unknown` 标注于**触发时机细节**（逐行 vs 逐单元格提交）——本轮证据到"列定义时注册守卫"为止。

### 3.4 尚存的 Unknown（诚实清单）

- `qword_1472C7440` 单例的精确类型名（606 处引用，未逐个排查归属；其双表语义已由 R677/R688 的数据侧结论交叉印证）。
- 州表为空时"静默放行"是否同时跳过 UI 高亮（只证明了返回 0，未看 UI 侧消费）。
- `sub_141CF6EA0` 格式化的 culture 选择（Invariant 与 Current 的区分未逐层看）。

---

## 四、验证与复算命令

```powershell
# 度量（replica/ 下）
python tools\metrics_report.py --skip-tests        # 本轮后：4 / 0 / 17 / 80（与基线一致）
dotnet test --filter "TypePresenceTriageTests|OriginalViewClassParityTests"   # 6/6 通过

# 定位链（根目录）
python analysis\disp32_scan_any.py --all license_csv    # 5 sites
python analysis\disp32_scan_any.py --all license_ctl    # 5 sites
python analysis\site_to_func.py 0x140F7739E 0x140F7784E # → sub_140F77350 / sub_140F777E0

# triage 新判定
python analysis\type_presence_triage.py                 # NOT_IN_FUNCTION_SET=2, RENAMED=7, ...
```

落盘证据：`analysis/csv_validator_host.c`、`csv_guard_helpers.c`、`csv_state_args.c`、
`csv_guard_delegates.json`、`license_control_main.c`、`license_refs_resolved.txt`。

---

## 五、下一步（按优先级，均待 YG 确认后执行）

1. **(b) 路径 B 实现**：`ProfileCsvEditorView.Validate()` 按上述四维规则补 Country/State 校验（半天工作量，规则全有据）。
2. **(a) 收尾**：把 `LoginControl`/`AuthWindow` 同族的其余 UNKNOWN 条目按裁决归档，让 17 条里 UNKNOWN 只剩业务侧的。
3. **方法沉淀**：`disp32_scan_any` 加 preset 生成器（从 pe_strings 批量喂键名），让"字符串→函数"对整个范围内的功能都一键可查。
4. 文档同步：`BLOCKERS.md` 补 §134（本轮）、`COMPLETION_AUDIT.md` 待 (b) 实现后重审。
