"""Record R716: the kind census, the correction to R714's reasoning, and what it says about code already shipped."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 145. 普查：`Getter` 100%、`Property` 100%、`Setter` 77.9% —— 我 R714 的推理错了，而它牵连已实现的成员

> R716。新增 `analysis/descriptor_kinds.py`、`analysis/descriptor_kind_census.py`。

### 一、本来要回答什么

R715 结尾留的问题：`AccountGroupView.Save` 带 Setter 而 `Close` 不带，差在哪？
线索是第三种描述符 `!Property`（AvaloniaProperty 的注册形态）。

### 二、四个视图一看，假设就破了

```
AccountGroupView  Close/Delete/GroupName/Save      全部 Getter/Property/Setter
CheckoutView      Checkout/Close/Next/OpenTracking/Previous/Properties
                                                   全部含 Property
ProxyGroupView    Close/Delete/Draft/Reset/Save/TimeSpans   全部含 Property
TaskGroupView     八个成员                                   全部含 Property
```

**`Close` 也是 `Getter/Property/Setter`** —— 而 R711 我据以实现的证据是「`Close` 只有 `Getter`」。
**那个「只有 Getter」是我自己的正则只取了每行第一处的产物。**

### 三、全表普查（819）

```
carries Getter    819  (100.0%)
carries Property  819  (100.0%)
carries Setter    638  ( 77.9%)

组合只有两种：  Getter+Property+Setter  638 (77.9%)
                Getter+Property         181 (22.1%)
```

**`Getter` 与 `Property` 是常量，只有 `Setter` 在变。**

### 四、更正 R714

R714 我写：「**78% 都是 G/S，所以方向字段几乎不带信息**」，并据此撤掉了文档里「该做成什么」那一列。

**这个推理错了**：78/22 **是真分裂**，不是常量。我把「多数」当成了「背景」。
真正不带信息的是 **`Property`（100%）** 和 **`Getter`（100%）**。

R714 撤掉那一列**依然是对的**（那一列按 G/S 推「可写属性」确实过度），**但理由要改**：
不是"方向没信息"，而是**"方向只说明绑定是双向的，不说明成员是什么类型"**。

### 五、这牵连到已经实现的成员

`Setter` 最可能编码的是**绑定模式（TwoWay）**，即"原版 XAML 会往这个成员写值"。

那么：

| 已实现 | 我做的形状 | 描述符要求 |
|---|---|---|
| `CheckoutView.Close`（R711） | `ICommand Close { get; }` **只读** | 带 Setter |
| `CheckoutView.Next` / `Previous` / `OpenTracking`（R472/R500） | `ICommand { get; }` 只读 | 带 Setter |
| `ReleaseView.Close`（R711） | `ICommand { get; }` 只读 | 带 Setter |

**这些实现与描述符不一致**：描述符说原版会写这个成员，我做的是只读。

**但把命令做成可写同样反常。** 所以**类型问题仍未解决** ——
`Setter` 只证明"会被写"，不证明"写进去的是什么"。

### 六、处置：不删、不改、标出来

**不回滚**：这些实现不算错，只是**证据不足以排除另一种读法**。
回滚同样是猜，而且会让 `undeclared` 计数倒退。

**做法是把话说清**：`docs/MEMBER_GAP_EVIDENCE.md` 的方向列现在有意义了（`Setter` 是唯一变量），
但它的含义是"双向绑定"，不是"该做成可写属性"。已在生成器里改注。

**并在 `BLOCKS` 里记下**：`ICommand` + 只读是一个**未排除的**读法，不是已验证的结论。

### 七、仍然 Unknown

- `Setter` 到底编码什么（绑定模式？还是"有 set 访问器"）：**Unknown** ——
  两种解释都能说明 77.9%，需要一个已知答案的样本去校准。
- `Property` 100% 出现意味着什么：**Unknown**（可能只是 Avalonia 对每个绑定都产出三种描述符）。
- 已实现的那几个 `ICommand` 是否该可写：**Unknown**，不猜。
"""

VERDICT = """

---

## 第 716 轮：普查 —— 常量与变量的区别，我上一轮看反了

### 本来要查 `!Property`

四个视图一看就破了假设：**每个成员都含 `Property`**，包括 `CheckoutView.Close`。

**而 R711 我据以实现的「`Close` 只有 Getter」是我自己的正则只取每行第一处的产物。**

### 全表普查（819）

```
Getter   100.0%
Property 100.0%
Setter    77.9%

组合只有两种：Getter+Property+Setter 638 / Getter+Property 181
```

**只有 `Setter` 在变。**

### 更正 R714

R714 我写「78% 都是 G/S，所以方向不带信息」—— **错。78/22 是真分裂，我把「多数」当成了「背景」。**
真正不带信息的是 `Getter` 与 `Property`（都 100%）。

撤那一列**仍然对**，但理由要改：不是「方向没信息」，而是**「方向只说明绑定是双向的，不说明成员是什么」**。

### 它牵连已实现的成员

| 已实现 | 形状 | 描述符 |
|---|---|---|
| `CheckoutView.Close`（R711） | `ICommand { get; }` 只读 | 带 Setter |
| `Next`/`Previous`/`OpenTracking`（R472/R500） | 只读 | 带 Setter |

**不一致。但不回滚** —— 它们不算错，只是**证据不足以排除另一种读法**；回滚同样是猜。
**把话说清，比改成一个别的猜测好。**

### 一句话

> 我把「78% 都有」读成了「没有区分力」。**78 对 22 是分裂，100 对 0 才是常量。**

> 普查一整列之后才发现：**我上一轮撤掉的结论，撤对了；撤的理由，错了。**

### 下一轮

找一个**已知答案的样本**去校准 `Setter` 的语义：在复刻件里挑一个我们确定是可写数据的成员
（如 `AccountGroup.Name`），看它有没有 Setter —— 有，说明 Setter ≈ 有 set 访问器；没有，说明是绑定模式。
"""


def main():
    for p, marker, text in ((P1, "R716", BLOCKER), (P3, "R716", BLOCKER), (P2, "第 716 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R716: descriptor kind census -- Getter 100%, Property 100%, Setter 77.9%\n\n"
         "Four views showed every member carrying Getter/Property/Setter, including CheckoutView.Close,\n"
         "whose 'Getter only' reading at R711 was an artefact of my regex taking the first match per line.\n\n"
         "Across all 819: Getter 100%, Property 100%, Setter 77.9%, and only two combinations exist\n"
         "(G+P+S 638, G+P 181). So the sole variable is Setter.\n\n"
         "This corrects R714's reasoning, not its outcome: I wrote that 78% Getter+Setter means the\n"
         "direction carries no information, but 78 against 22 is a split -- the constants are Getter and\n"
         "Property at 100%. Removing the 'what to make it' column was still right, for a different reason:\n"
         "direction says the binding writes to the member, not what the member is.\n\n"
         "Consequence for shipped code: Close, Next, Previous and OpenTracking were implemented as\n"
         "getter-only ICommand while their descriptors carry Setter. They are not reverted -- they are not\n"
         "wrong, only under-evidenced, and reverting would be a different guess -- but the inconsistency is\n"
         "now on record."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
