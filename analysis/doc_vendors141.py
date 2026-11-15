import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 六道墙的普查：检测在、存储在，**调用**在两道（第 141 轮）

上一轮发现的缺陷（「检测在、存储在，中间的调用不在」）用同一把尺子扫一遍全部六个 vendor。

| vendor | 检测标记 | cookie | 调用已接？ |
|---|---|---|---|
| **cloudflare** | `cf-chl` / `server: cloudflare` | `cf_clearance` | **是**（R140） |
| **kasada** | `kpsdk` | `kpsdk` | **是**（R141） |
| imperva | `_Incapsula_Resource` | **无** | 否 |
| datadome | `datadome` | `datadome` | 否 |
| perimeterx | `px-captcha` | **无** | 否 |
| queue-it | `queue-it` | `queue-it-set-cookie` | 否 |

### 四个缺口不是同一种缺口

| vendor | 缺的是 | 要解开需要什么 |
|---|---|---|
| **datadome** | 协议（主机已知：`datadome.cybersole.io`） | 一次抓包 —— 与 R140 之前的 Cloudflare 同型 |
| **imperva** | 连 cookie 都没有 | 先找到它的 cookie 名 |
| **perimeterx** | 镜像里就是空的 | 保持空 —— **故意留白比猜一个 `_px` 更诚实** |
| **queue-it** | 不是挑战，是**排队** | **等待**，不是求解 |

> 最后一条最容易被写错：把 Queue-it 当验证码去「解」，会把一个排队问题变成一次失败。

### `KasadaClearance`：与 Cloudflare 的修法一模一样

```csharp
if (!IsKasada(c.Session)) return StepOutcome.Success();
var token = await runner.GetAsync(pageUrl, ct);
c.Session.Vars["kasada.status"] = token.Status;
c.Session.Vars["kasada.mode"]   = token.Mode.ToString();
if (!token.Usable) { c.Emit(token.Status, "antibot"); return StepOutcome.Success(); }
c.Session.Vars["kasada.token"] = token.Token;
c.Session.Cookies["kpsdk"]     = token.Token;   // 只有当镜像确实给了 cookie 名才写
```

**token 带着它的来路（`Mode`）一起存** —— 拿到回退 token 的调用方有权知道这一点。

### 一条从三轮里长出来的规则

```
detection and storage are cheap and were already present;
the call between them is the work
```

检测和存储是最便宜的部分，而且**它们早就在那儿**；真正的工作是中间那次调用。
'''

if "## 六道墙的普查" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("vendor audit documented")
else:
    print("already present")
