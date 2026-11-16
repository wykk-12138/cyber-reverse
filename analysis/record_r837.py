"""Record R837: the image embeds DotNetBrowser; the replica substitutes its own TLS plus external CDP."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 261. 架构级差异：**镜像内嵌 DotNetBrowser，复刻件自建 TLS + 外部 CDP**

> R837。未改产品代码。**这条不是缺口，是一处有意的替代 —— 但此前没有单独记过。**

### 一、怎么发现的

R836 里 `PopMartBrowser` 这个类型名让我去查「`*Browser` 是不是一套通用结构」。

```
ida.py str RpcHandler   -> 1 match: PopMartRpcHandler   （PopMart 独有，不是通用层）
ida.py str Browser      -> 10 matches，distinct 记号两个：DotNetBrowser / dll8DotNetBrowser
```

**然后查 `DotNetBrowser`，出来几百条 —— 不是十个。**

### 二、镜像里它有多深

| 层 | 证据 |
|---|---|
| **UI 绑定** | `DotNetBrowser.AvaloniaUi.v12.dll` · 也有 `Wpf` / `WinForms` / `WinUi3`（依赖元数据） |
| **内部 RPC** | `dnb::DotNetBrowser.Internals.Ipc.IRpcCallbackMessage<DotNetBrowser.Internal.Rpc.BrowserId, …>`（上百条） |
| **视图实现** | `DotNetBrowser.Browser.IBrowserViewImpl.OnFocusGained` / `DeinitializeView` |
| **屏幕投射** | `DotNetBrowser.Cast.IMediaReceivers.get_AllAvailable` |
| **自动填充** | `DotNetBrowser.Autofill.Suggestion` · `CreditCardInfo!Getter` · `AddressOrFullname!Getter` |
| **证书选择** | `DotNetBrowser.Net.Certificates.Certificate` · `SelectCertificateDialogViewModel` |
| **codegen 标记** | `protoc-gen-dotnetbrowser` |
| **强名公钥** | `DotNetBrowser.Core, PublicKey=002400…` |

**所以镜像里有一个完整的、进程内的 Chromium。**

### 三、复刻件那边

**`grep DotNetBrowser` 在复刻件只命中一处，而且是注释：**

```
ChromiumBridge.cs:13  /// original gets away with "local generation" because it ships DotNetBrowser/Chromium. This
```

**七个 `csproj` 的 `PackageReference` 里没有 DotNetBrowser。** 只有：
`Newtonsoft.Json` · `CommunityToolkit.Mvvm` · `BouncyCastle.Cryptography` · `MailKit` ·
`Microsoft.Extensions.DependencyInjection` · `Jint` · `Avalonia`（含 Fluent/Inter/Diagnostics）· xunit。

**所以复刻件的做法是：**
**自己写 TLS（`Tls12Client` / `BouncyTls` / `Ja3` / `Http2` / `HpackHuffman`），浏览器走外部 Chrome 的 CDP（`ChromiumBridge`）。**

### 四、这不是遗漏

**`ChromiumBridge.cs:13` 的注释说明这是一次有意的取舍** ——
**镜像靠「随包带一个 Chromium」拿到本地生成能力，复刻件不这么做，改为自己实现。**

**所以这条的正确措辞是：**

> **同一项能力（在进程内跑一个能通过风控的真浏览器），两边用了不同的手段。**
> **镜像买了一个（DotNetBrowser 是商业库，需授权）；复刻件自己写了传输层、并复用系统 Chrome。**

**判据上这属于「允许不同」的范畴（goal 写明「命名可不同，不要求字节级相同」），
但它是**优先级 ③（请求与指纹层）最重要的一个设计事实**，此前没有被单独记下来。**

### 五、它解释了 R835 的一个悬案

**`popDraw.json` 的 xref 是 0。** 现在有了解释的方向：
**抽签数据可能是 `PopMartBrowser` 里的页面脚本读的 —— 那是在 Chromium 里跑的 JS，不是 C# 代码，
所以 IDA 看不到对它这个字面量的引用。**

**这是 Inference（中），本轮没验。**

### 六、验证

```
ida.py str RpcHandler      -> 1（PopMartRpcHandler）—— 不是通用层
ida.py str Browser         -> 10 matches
ida.py str DotNetBrowser   -> 数百条，含 AvaloniaUi.v12 / Internals.Ipc / Cast / Autofill / 强名公钥
复刻件 grep DotNetBrowser  -> 1 处，且是注释（ChromiumBridge.cs:13）
复刻件 7 个 csproj         -> 无 DotNetBrowser PackageReference
本轮未改产品代码
七项度量沿用
```

### 七、仍然 Unknown

- **DotNetBrowser 的授权状态**：**Unknown** —— 它是商业库，**镜像带了 `.dll` 不代表有分发权。**
  **这条只影响「要不要照搬」，不影响已做的替代是否成立。**
- **`Cast.IMediaReceivers` 被用到什么程度**：**Unknown** —— 名字是屏幕投射，
  **可能是镜像的「浏览器视图」用，也可能只是库的完整字符串（未被裁掉）。**
- **复刻件的替代在等价性上够不够**：**Unknown** ——
  **`PerformanceTests` 量的是循环比、`TlsTransportPerformanceTests` 量的是自有 TLS 对 SChannel 比，
  但没有一条量「能不能通过某站的风控」。**
- **`popDraw.json` 是否真由页面脚本读**：**Inference（中）**，未验。

### 八、教训

**我查 `Browser` 时先得到 10 条，于是差点写下「浏览器相关就这十个」。
真正的东西在 `DotNetBrowser` 这个更长、更具体的词下面 —— 有几百条。**

**和 R836 的教训是同一条的第三个变体：**
**R830 按站名搜漏了 `/shop/v1`；R836 按形态筛漏了 `POPMART-RESERVATION`；**
**这一轮按短词搜只看到 10 条，而全貌在长词下面。**

**共同点：我选的检索词决定了我能看到什么，而我没有先问「这个词是最具体的那一个吗」。**
"""

VERDICT = """

---

## 第 837 轮：镜像内嵌 DotNetBrowser，复刻件自建 TLS + 外部 CDP

### 怎么发现的

R836 的 `PopMartBrowser` 让我查「`*Browser` 是不是通用结构」：

```
str RpcHandler  -> 1（PopMartRpcHandler，PopMart 独有，不是通用层）
str Browser     -> 10 matches
str DotNetBrowser -> 数百条      ← 全貌在长词下面
```

### 镜像里它有多深

`AvaloniaUi.v12`（也有 Wpf/WinForms/WinUi3 的依赖元数据）· `Internals.Ipc.IRpcCallbackMessage`（上百条）·
`Browser.IBrowserViewImpl` · **`Cast.IMediaReceivers`（屏幕投射）** · `Autofill.*`（含 `CreditCardInfo`）·
`Net.Certificates.Certificate` · `protoc-gen-dotnetbrowser` · 强名公钥

**一个完整的、进程内的 Chromium。**

### 复刻件那边

**`grep DotNetBrowser` 只命中一处，且是注释：**

```
ChromiumBridge.cs:13  /// original gets away with "local generation" because it ships DotNetBrowser/Chromium.
```

**七个 csproj 无 DotNetBrowser 包。** 复刻件自己写 TLS（`Tls12Client`/`BouncyTls`/`Ja3`/`Http2`/`HpackHuffman`），
浏览器走外部 Chrome 的 CDP。

### 这不是遗漏

**注释说明是有意取舍。正确措辞：同一项能力用了不同手段 —— 镜像买了一个商业库，复刻件自己写了传输层并复用系统 Chrome。**

**goal 写明「命名可不同，不要求字节级相同」，所以这在允许范围内；但它是优先级 ③ 最重要的设计事实。**

### 它解释了一个悬案

**`popDraw.json` 的 xref 是 0** —— 抽签数据可能是 `PopMartBrowser` 里的**页面脚本**读的，在 Chromium 里跑，
**所以 IDA 看不到对那个字面量的引用。Inference（中），未验。**

### 仍然 Unknown

**DotNetBrowser 的授权状态**（镜像带了 dll 不代表有分发权；只影响「要不要照搬」）·
**`Cast.IMediaReceivers` 被用到什么程度**（可能只是库未裁掉的完整串）·
**复刻件的替代在等价性上够不够**（现有性能度量都没量「能不能过某站风控」）

### 教训

**我查 `Browser` 得到 10 条，差点写下「浏览器相关就这十个」；真正的东西在 `DotNetBrowser` 这个更长更具体的词下面。**

> **检索词决定了能看到什么。而我没有先问「这个词是最具体的那一个吗」。**
> **R830 按站名搜漏了 `/shop/v1`；R836 按形态筛漏了 `POPMART-RESERVATION`；这一轮按短词搜只看到 10 条 —— 三次都是同一个错，换了三个筛子。**
"""

BACKLOG_ADD = """

## 优先级 ③ — 架构事实：镜像内嵌 DotNetBrowser（R837）

| | 镜像 | 复刻件 |
|---|---|---|
| 进程内浏览器 | **DotNetBrowser**（数百条串：`AvaloniaUi.v12` · `Internals.Ipc` · `IBrowserViewImpl` · `Cast.IMediaReceivers` · `Autofill.*` · 强名公钥） | **无**（7 个 csproj 无该包） |
| HTTP/TLS | 由库承担 | **自建** `Tls12Client` · `BouncyTls` · `Ja3` · `Http2` · `HpackHuffman` |
| 浏览器驱动 | 进程内 | **外部 Chrome 经 CDP**（`ChromiumBridge`） |

**`ChromiumBridge.cs:13` 的注释说明这是有意取舍** —— 镜像靠随包带 Chromium 拿到本地生成能力，复刻件改为自己实现。
**goal 允许「命名可不同」，所以这在范围内；但它是优先级 ③ 最重要的设计事实。**

**副作用解释**：`popDraw.json` 的 xref 为 0 —— 可能由页面脚本在 Chromium 里读，**IDA 看不到**。Inference（中）。

| 仍 Unknown | |
|---|---|
| DotNetBrowser 授权状态 | 带 dll ≠ 有分发权；只影响「要不要照搬」 |
| `Cast.IMediaReceivers` 实际使用程度 | 可能是库未裁掉的串 |
| 替代方案等价性 | **现有性能度量都没量「能不能过某站风控」** |

### 纪律（第三次同一形态）

**检索词决定能看到什么。搜 `Browser` 得 10 条，搜 `DotNetBrowser` 得数百条。**
**R830 按站名漏 `/shop/v1`；R836 按形态漏 `POPMART-RESERVATION`；R837 按短词只看到 10 条。**
**先问：这个词是最具体的那一个吗。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R837", BLOCKER)
    ensure(RSTATUS, "R837", BLOCKER)
    ensure(RVERDICT, "第 837 轮", VERDICT)
    ensure(BACKLOG, "R837", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R837" not in h:
        h += ("\n## R837 补充 — 架构事实：DotNetBrowser\n\n"
              "**镜像内嵌 DotNetBrowser**（数百条串）；**复刻件不引用该包**（1 处注释 + 7 个 csproj 无此包）。\n"
              "复刻件的替代：自建 TLS（`Tls12Client`/`BouncyTls`/`Ja3`/`Http2`）+ 外部 Chrome 经 CDP。\n"
              "**`ChromiumBridge.cs:13` 注释表明是有意取舍**，在 goal 允许范围内，但是优先级 ③ 最重要的设计事实。\n"
              "**检索词纪律**：搜 `Browser` 得 10 条，搜 `DotNetBrowser` 得数百条 —— 先问「这个词是最具体的吗」。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R837"), (RSTATUS, "R837"), (RVERDICT, "第 837 轮"), (BACKLOG, "R837")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R837: the image embeds DotNetBrowser, and the replica substitutes its own TLS plus external CDP\n\n"
         "R836's PopMartBrowser prompted a check of whether the *Browser naming is a shared structure. RpcHandler"
         " returns exactly one match, PopMartRpcHandler, so RPC handlers are PopMart-specific rather than a layer. Browser"
         " returns ten matches, which nearly became the answer -- but the two distinct tokens were DotNetBrowser and its"
         " assembly name, and searching that longer word returns hundreds.\n\n"
         "The image carries a complete in-process Chromium: the Avalonia v12 binding along with Wpf, WinForms and WinUi3"
         " dependency metadata; the internal IPC layer with several hundred IRpcCallbackMessage instantiations;"
         " IBrowserViewImpl for the view contract; Cast.IMediaReceivers, which is screencast; Autofill with credit-card"
         " and address suggestions; certificate selection dialogs; a protoc codegen marker; and a strong-name public key.\n\n"
         "The replica references none of it. DotNetBrowser appears in exactly one place, a comment in ChromiumBridge"
         " explaining that the original gets away with local generation because it ships DotNetBrowser and Chromium, and"
         " none of the seven project files carries the package. What the replica does instead is write its own transport"
         " -- Tls12Client, BouncyTls, Ja3, Http2, HpackHuffman -- and drive an external Chrome over CDP.\n\n"
         "That comment is why this is a substitution rather than an omission. The same capability, running a browser that"
         " can pass a site's checks, is reached two ways: the image buys one, the replica writes the transport and reuses"
         " the system browser. The goal allows naming to differ and does not demand byte identity, so this sits inside the"
         " permitted range -- but it is the single most important design fact in the request-and-fingerprint layer and had"
         " never been recorded on its own.\n\n"
         "It also offers an explanation for an open question. popDraw.json has no cross-reference, and if the draw feed is"
         " read by page script inside the embedded browser then IDA would not see a C# reference to that literal at all."
         " That is inference, not observation, and was not tested.\n\n"
         "Unknown: DotNetBrowser's licence status, since shipping the assembly does not establish a right to redistribute"
         " it, though that affects only whether to copy the approach rather than whether the substitute stands; how far"
         " Cast is actually used, which may simply be strings the trimmer kept; and whether the substitute is equivalent"
         " in the sense that matters, because the existing performance tests measure loop ratios and own-TLS against"
         " SChannel but none of them measures passing a real site's checks.\n\n"
         "The lesson repeated for the third time in a different filter: R830 searched by site name and missed /shop/v1,"
         " R836 filtered by URL shape and missed POPMART-RESERVATION, and this round searched a short word and saw ten"
         " strings where the full picture sat under a longer one. The word chosen determines what can be seen, and I did"
         " not first ask whether it was the most specific word available.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
