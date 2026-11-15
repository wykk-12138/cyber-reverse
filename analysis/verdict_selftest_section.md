### 工具也要被工具检查：`mutation-check.py` 的五条自检

R143–R148 六轮里找到五个假绿，全在**守护测试**里。这一轮问第一次：
**那个找假绿的工具，自己会不会误判？**

### 五条已知答案的输入

`tools/mutation-self-test.py` 给 `mutation-check.py` 喂五种变异，每种都写明应该得到什么判决：

| 用例 | 期望 | 说明 |
|---|---|---|
| 一个真变异 | `guard fired` | 对照组——证明循环是活的 |
| 一个不存在的 anchor | `SKIPPED` | 变量改名让所有 anchor 失配时，不能读成「一切正常」 |
| `--filter` 匹配 0 个测试 | `GUARD IS DECORATIVE` | **`dotnet test` 在 0 命中时退出码是 0** |
| 改 JS 字符串字面量 | `guard fired` | 那个字面量是 verbatim string，随便写什么都还是合法 C# |
| 改真的 C# 语法 | `DID NOT COMPILE` | 只有编辑 C# 本体才会让构建失败 |

**第三条是这一轮最重要的发现**：

```
dotnet test --filter "FullyQualifiedName~NoSuchTestXYZ12345"
exit=0
```

**测试名写错，`dotnet test` 报告成功。** 所以 `mutation-check.py` 把它判成
`GUARD IS DECORATIVE`（「测试没红」＝「守护无效」）——**这个判定是对的**，
因为它把「没测」和「测了但通过」一视同仁。

**如果当初把 `code == 0` 判成 `fired`，一个拼写错误就会让整张表全绿。**

### 第 4 和第 5 条分开是因为第一次写错了

第一版只有一条「不能编译」，用的是：

```python
"replace": "                value: function getVoices() { return this is not C#; },",
```

**它是 JS 字符串里的内容**，C# 编译器根本不看。所以它编译通过、守卫读到、
**fired** ——而我的期望是 `DID NOT COMPILE`。

**拆成两条**：

- 改字面量 → 能编译 → `fired`（记录这个事实）
- 改 `public async ValueTask DisposeAsync()` 成 `( { {` → 编译失败 → `DID NOT COMPILE`

**第二条的 anchor 第一次还写错了**：4 个空格写成 8 个，报 `ANCHOR MISSING`。
**工具自检的第一步，是它自己的 anchor 也得对。**

### 5/5

```
[ok  ] control: a real mutation must fire                    guard fired
[ok  ] an anchor that does not exist must be skipped         SKIPPED
[ok  ] a test filter matching nothing                        GUARD IS DECORATIVE
[ok  ] a mutation inside the JS literal still compiles       guard fired
[ok  ] a mutation in real C# that cannot compile             DID NOT COMPILE
== 5/5 classified correctly ==
```

### 接进 `verify.ps1 -Full`，跑在变异检查**之前**

```powershell
if (Test-Path 'tools\mutation-self-test.py') {
    $self = & $py 'tools\mutation-self-test.py' 2>&1 | Out-String
    $correct = ([regex]::Matches($self, '\[ok  \]')).Count
    $wrong   = ([regex]::Matches($self, '\[FAIL\]')).Count
    if ($wrong -gt 0) {
        Check 'mutation self-test' $false "$correct right, $wrong wrong — the verdicts below cannot be trusted"
    }
    …
}
```

**顺序是有意的**：自检先跑。如果分类器本身坏了，**下面的 17 条判决不值得读**。

### 完整的 `-Full`

```
unit tests          PASS   exit 0
doc docs\VERDICT.md PASS
mutation self-test  PASS   5/5 classified correctly
mutation guards     PASS   17 fired, 0 decorative, 0 did-not-compile, 0 skipped
VERDICT: all checks passed
```

**四层**：

1. 单测（行为）
2. 文档锚点（一致性）
3. **自检**（工具可信吗）
4. 变异（守护有效吗）

---
