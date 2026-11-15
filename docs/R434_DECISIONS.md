# R434 裁决：MonitorView 五条怎么做 + 那个口径盲区怎么补

## 0. 选 **A（结构对等 + 可观测行为 + 显式钩子）**，但加四条约束

理由：`bind_scope` 只证明"属性存在"，但 `Getter/Setter/Property` 三串齐全说明这五个成员是**XAML 里的绑定目标**
（列表页 + 选中项驱动的动作），"动作作用于当前选中项"是**结构可推**的，不是猜行为。
所以 `View` / `OpenFilter` 这两条有模型证据的应当真做；其余三条做**显式钩子**而不是静默空实现。

### 约束 1：可观测的两条要真做，并留可重算证据

- `View`：命令触发后**选中项详情可见**（`MonitorView.SelectedEvent` → 详情区文本/字段变化），测试断言"详情内容 == 当前选中项"。
- `OpenFilter`：命令触发后**暴露 `Settings.MonitorFilters`**（`MonitorView.Filters` 返回该集合，测试断言同一实例/同一条目）。
- 这两条在 `PARITY_CLAIMS.md` 记 `authority: tool-evidence`（绑定表串地址 + 模型串地址）+ `command:` 具体用例名。

### 约束 2：三条钩子必须"不假装成功"

`OpenUrl` / `LinkChange` / `Quicktask`：

```csharp
/// <summary>structure only — behaviour unknown (claim C-monitor-quicktask). The host may supply a delegate;
/// when none is supplied invoking this command performs no side effect and records why.</summary>
public ICommand Quicktask => _quicktask ??= new RelayCommand<MonitorEvent>(e => RunHook(ref _quicktaskRun, e));
```

要求：
- 钩子签名一律 `Action<MonitorEvent>?`（或 `Func<MonitorEvent, string?>`），**默认 null**；
- 未注入时**不得**产生任何外部副作用（不打开浏览器、不写剪贴板、不发请求）；
- 命令触发时**必须把当前选中项交给钩子**，测试断言这一点（"拿到的是当时选中项"）；
- 代码注释与 `PARITY_CLAIMS.md` 的 claim id 互相指认（注释里写 claim 编号）。

### 约束 3：Unknown 记账要结构化，且与代码互指

`PARITY_CLAIMS.md` 增三条（`authority: unknown`，`gap_reason` 写清缺什么）：

| claim | 目标行为 | 缺什么证据 |
|---|---|---|
| C-monitor-openurl | 打开商品 URL 的方式（浏览器/内置） | 需主界面 GUI 观察或伪代码级对照 |
| C-monitor-linkchange | "Link Change" 作用于什么（链接替换？批量？） | 同上；locale 有 `Monitor.LinkChange` 文案但无语义 |
| C-monitor-quicktask | Quicktask 的目标（任务创建？剪贴板？） | 同上；`Monitor.LaunchQuicktask` 只有文案 |

并加一条守卫测试 `MonitorViewBehaviourPins`：断言三条 claim 在 `PARITY_CLAIMS.md` 里存在、`authority == unknown`、
且 `MonitorView` 源码里对应成员注释提到该 claim 编号。**代码与账本任一方被删，测试就红。**

### 约束 4：先 snapshot，再一次性落块

`python tools/snapshot.py` → 整块锚点替换（禁止行号手术）→ 只跑相关用例 → 再跑一次 `bind_scope`。

---

## 1. 你发现的那个盲区：**必须修工具**（真盲区）

> `Cybersole.Models.Input` 类型整体不存在，但因为成员名 `Type` 在源码别处满地都是，`bind_diff` / `bind_scope` 都不报。

这是**第三类缺口**，与「名字级 16」「类型级 4」都不同：**类型级缺失（type absent）**。

做法：

1. `replica/tools/bind_diff.py` 增一个独立小节（或 `--type-presence` 开关），对绑定表 174 个类型逐个检查
   **源码里是否存在同名类型声明**（`class|record|struct|enum|interface <Name>`，含嵌套/命名空间后缀匹配），
   输出：
   ```
   type presence: 174 declared in bindings, N present in source, M absent
     ABSENT  Cybersole.Models.Input        (members: Type)
     ABSENT  ...
   ```
2. 该数字进 `docs/METRICS.md`（`metrics_report.py` 一并调用），成为**第四个度量**：
   `类型缺失 M`。
3. `docs/GOAL.md` 判据 a 补一句：`类型缺失 → 0`（或每条都写 Unknown 理由）。
4. 本轮把 `Models.Input { Type }` 补上（它有绑定串证据），把它从 ABSENT 名单里消掉，剩下的 ABSENT 进 backlog。

> 这条工具改动属于「现有不够用」的正当扩展：`bind_scope` 只查"成员是否在同一类型 body 内"，
> 无法发现"类型根本不存在"。文件头补一句说明。

---

## 2. 一句话

> **选 A —— 有模型证据的两条真做，没证据的三条做显式钩子并逐条记 Unknown；
> 你发现的类型缺失盲区，用第四个度量（type presence）钉死，别再靠"成员名满地都是"遮过去。**
