# R504 卡点：NativeAOT 的元数据没有 xref，行为证据链在数据段上断开

> 写于 R504（2026-11-14 23:30 前后）。这份文档只回答一件事：
> **B 类 31 个成员的"行为"还能不能拿到？** 结论是不能，用现有工具。下面给证据，最后是一个需要 YG 做的选择。

---

## 1. 一句话结论

`Cybersole.exe` 是 .NET 10 NativeAOT。它把编译期绑定描述符以**相对偏移**的方式摊在只读数据段里，
**没有任何交叉引用指向它们**。所以"从描述符找到引用它的注册代码、再反编译那个代码"这条常规路线，
在这份二进制上**从第一步就断了**。

这不是"还没找到"，是"链在数据段这一侧不成立"。

---

## 2. 证据（可复现）

### 2.1 工具就绪（排除"工具没开"这个可能）

```
python analysis\ida.py health
```

```json
{"status":"ok","idb_path":"D:\\projects\\cyber-reverse\\target\\Cybersole.exe.i64",
 "module":"Cybersole.exe","imagebase":"0x140000000",
 "auto_analysis_ready":true,"hexrays_ready":true}
```

`auto_analysis_ready` 与 `hexrays_ready` 都是 `true` —— 分析完成，反编译器可用。

### 2.2 描述符拿到了

```
python analysis\ida.py str "AccountGrid.*Clear"
```

命中两块（`n=2`），其中 `0x14320c54d` 是一个长串，里面连续摊着：

```
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Add!Getter
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Add!Setter
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Clear!Getter
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Clear!Setter
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Edit!Getter
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Edit!Setter
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Delete!Getter
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Delete!Setter
```

另一块 `0x1436389fc` 是：

```
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Clear!Property
Cybersole.Ui.Views.Accounts.AccountGrid,Cybersole.Edit!Property
```

**描述符本身完全可读** —— 这也是 R463–R490 能确认 951 条成员、215 个类型的依据。

### 2.3 但没有任何东西指向它们

```
python analysis\ida.py xrefs 0x14320c54d
python analysis\ida.py xrefs 0x1436389fc
```

```
[{"addr":"0x14320c54d","xrefs":[],"more":false,"xref_count":0,
  "message":"No cross-references to this address"}]
[{"addr":"0x1436389fc","xrefs":[],"more":false,"xref_count":0,
  "message":"No cross-references to this address"}]
```

**两次都是 0。**

---

## 3. 这不是找错地址 —— 它和已记录的数字对得上

`docs/PARITY_PRODUCT.md` 的"零直接 xref 对照"一节记着：**原版的零直接 xref 比例是 1.1%**，
复刻件是 3.6%。当时那个数字只是统计；**R504 给了它的机制解释**：

> NativeAOT 不把这些元数据放进会被 `call`/`lea` 直接引用的位置，
> 而是让运行期按**基址 + 偏移**去算。偏移不是交叉引用。

所以：

| 想拿的东西 | 为什么拿不到 |
|---|---|
| 描述符 → 引用它的注册代码 | 描述符无 xref |
| 属性的 setter 做什么 | 编译期内联，没有独立函数体 |
| `ICommand` 的行为 | 藏在委托初始化点；定位那个点要靠类型信息，类型信息同样无 xref |

---

## 4. 它影响哪两条结论

1. **B 类 31 个成员**（`Save`×6 / `Clear`×6 / `Add`×6 / `Delete`×3 / `OpenUrl`×2 / 其他×8）：
   复刻件里连同名方法都没有，要补就得"写一个实现"，而写出来的会是**猜测**。
   见 `replica/docs/BINDING_BACKLOG.md` 的「42 条」一节。
2. **`PARITY_CLAIMS.md` 的 C7c「每个函数功能相等」**：一直是 `unknown`。R504 确认了这个 `unknown` 的
   **技术依据**，它不是因为没查，是因为这条证据链不存在。

**结构对等 ≠ 行为对等** 这句话，在这里第一次有了硬理由，而不只是纪律要求。

---

## 5. 剩下的两条路

### 路 A：接受「结构对等 + 行为 Unknown」

- 形状已经清到 143 条，剩下的全部有定性（A 类硬约束 7 / B 类需行为证据 31 / 已做 4）。
- 判据 a 明确允许"每条若不可得则写 Unknown + 缺什么"。B 类可以按这个格式结案。
- **代价**：C7c 永远是 unknown，`objective` 的第二句（每个函数功能相等）无法声称达成。

### 路 B：运行期差分

不看静态代码，让**原版真的执行一次**这些动作，观察它改了什么。

- 例如：打开原版 → 在有数据的 Accounts 页点 `Clear` → 看 `%APPDATA%\Cybersole` 下哪个文件变了、怎么变。
- **这是唯一能把 B 类从 unknown 变成已知的路线**，因为行为在运行期是可观察的。
- **它需要登录凭据**（原版不登录进不到有数据的页面）。
- goal 明确把"原版登录凭据"列为**可以停下来等 YG 的两件事之一**。

**注意**：运行期观察只读 `%APPDATA%\Cybersole`，不写入 —— 这条纪律不变。

---

## 6. 需要 YG 决定的一件事

> **走 A 还是走 B？**

- **A**：我现在就能把 B 类 31 条按「结构差异 + 行为 Unknown + 缺什么证据」写进 backlog 和 claim 表，
  然后按判据 a 结案，转入判据 b/c/d/e 的收尾验证。
- **B**：需要你给原版登录凭据（或允许我只读观察已登录的 `Cybersole` pid 22564 的会话），
  我就能拿运行期差分补上行为证据。

**在等到答复之前，我不会推进 B 类**，也不会替 B 类编实现 —— 那会违反 `Observation` 纪律。
其它能做的（判据 b/c/d/e 的验证）我会继续做，不受这个选择影响。
