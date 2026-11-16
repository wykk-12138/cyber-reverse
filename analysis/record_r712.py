"""Record R712: the 44-member evidence table, generated so it cannot drift."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 141. 44 条未声明成员：**全部有原版描述符**，方向也拿到了

> R712。新增 `analysis/member_descriptors.py`、`analysis/write_member_gap_doc.py`、
> 生成的 `docs/MEMBER_GAP_EVIDENCE.md`。

### 一、为什么要一次性铺开而不是逐条判

R709 我看了十二个名字，判断「这不像真成员，是提取器造的」，写进了 BLOCKERS；R710 被字符串池证否。
**逐条凭印象判，就会重复那次错。** 所以这次把整个桶的证据一次铺开，每一行都能用一条 grep 核对。

### 二、索引自检（先自检，再出结论）

```
pe_strings.txt 里的 Cybersole 描述符 : 1457 条
索引出的 (类型, 成员) 键              : 819
绑定表 xaml_bindings.json 的成员数   : 819
```

**819 = 819**：两个独立来源给出同一个数。这是索引可用的第一条证据 —— 如果它给出 800 或 830，
下面那张表就不能信。

### 三、结论

```
源码未声明、且原版确有描述符 : 44
源码未声明、原版无描述符     : 0
```

**44 条全部是原版真的绑定过的名字。** 方向分布：

| 描述符方向 | 条数 | 该做成什么 |
|---|---|---|
| `Getter` | 26 | 只读属性，或 `ICommand`（Avalonia 的命令也走 Getter） |
| `Getter/Setter` | 18 | 可读写属性 |

### 四、这张表改变了什么

改前：44 条「源码没声明」——**这是关于复刻件的陈述，不是关于原版的**。
改后：44 条「原版绑定过、复刻件没声明」——**这是一个可以动手的缺口定义**。

而且方向是新的信息：`Getter/Setter` 那 18 条（`BotTask.Running`、`Notification.Message`/`Type`、
`EditValue`1` 的 12 个、`State.Name`、`CreateModel.Inputs`、`ProxyGroupView.Reset`/`Save`…）
**必须做成可写属性**，不是 `ICommand` —— 这一点只从「没声明」三个字看不出来。

### 五、验证

```
python tools/metrics_report.py            1624 通过 / 0 失败 / 0 跳过（代码未动）
python analysis/audit_claims.py           inconsistencies: 0
python analysis/member_descriptors.py     44 / 44 有描述符
```

**本轮没有改复刻件代码**，所以四项度量与 R711 一致（4 / 0 / 17 / 78 / 0）。
**这不是"没有进展"**：进展是把 44 个未知变成了 44 个有据可查、有方向可依的缺口。

### 六、仍然 Unknown

- **行为**：只证明原版绑定过这些名字，不证明它们做什么。**一律 Unknown。**
- `EditValue`1` 那 12 个带数字后缀的名字承担什么语义：**Unknown**（真实存在，含义未知）。
- 26 条 `Getter` 里哪些是 `ICommand`、哪些是只读数据属性：**Unknown** ——
  描述符只说 Getter，区分要看原版的反编译，未做。
"""

VERDICT = """

---

## 第 712 轮：44 条全部有据，方向也拿到了

### 先自检再出结论

```
pe_strings.txt 里的 Cybersole 描述符 : 1457 条
索引出的 (类型, 成员) 键              : 819
绑定表 xaml_bindings.json 的成员数   : 819
```

**819 = 819** —— 两个独立来源同数，索引才可信。

### 结论

```
源码未声明 + 原版有描述符 : 44
源码未声明 + 原版无描述符 : 0
Getter 26 条 / Getter+Setter 18 条
```

### 这张表改变了什么

改前：44 条「源码没声明」——**关于复刻件的陈述**。
改后：44 条「原版绑定过、复刻件没声明」——**可动手的缺口**。

方向是新的信息：`Getter/Setter` 那 18 条**必须做成可写属性**，不是 `ICommand`。
**这一点只从"没声明"三个字看不出来。**

### 验证

```
完整套件 1624 通过 / 0 失败
audit_claims 0
代码未动 -> 四项度量与 R711 一致（4 / 0 / 17 / 78 / 0）
```

### 一句话

> 本轮没改代码，但把 44 个未知变成了 44 个有据可查、有方向可依的缺口。

> **「没声明」是关于我的陈述，「原版绑定过而我没声明」才是关于差距的陈述。
> 同一批名字，换一个证据来源，就从待办清单变成了施工图。**

### 下一轮

按方向分两批做：先 18 条 `Getter/Setter`（可写属性，最机械），再 26 条 `Getter`
（其中哪些是 `ICommand` 需要看反编译，别一律当命令）。
"""


def main():
    for p, marker, text in ((P1, "R712", BLOCKER), (P3, "R712", BLOCKER), (P2, "第 712 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R712: every one of the 44 undeclared members has an original descriptor\n\n"
         "Built an index of the original's compiled-XAML descriptors from pe_strings.txt: 1457 entries\n"
         "across 819 (type, member) keys -- exactly the binding table's member count, which is the first\n"
         "reason to trust the index. Against the 44 members the replica's source does not declare, all 44\n"
         "have a descriptor (26 Getter, 18 Getter/Setter) and none is missing.\n\n"
         "docs/MEMBER_GAP_EVIDENCE.md is generated from that index so a reader can grep any row and the\n"
         "table cannot drift. This exists because R709 judged these same names implausible and wrote a\n"
         "wrong conclusion into BLOCKERS; the pool refuted it at R710.\n\n"
         "The change is what the rows now say: 'the source does not declare it' describes my code, while\n"
         "'the original binds it and I do not declare it' describes the gap. The direction is new too --\n"
         "18 of them must be writable properties, not ICommand."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
