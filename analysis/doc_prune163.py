import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 剪枝：同一成员，一个 claim 装、另一个 claim 删（第 163 轮）

原版注入了 NAV 之后紧跟着一句注释：

```
// Actually removed, not hidden behind a trap. Blink exposes a pile of interfaces WebKit has
// never shipped -- userAgentData, getBattery, connection, bluetooth, usb, hid, serial, xr,
// deviceMemory -- and browserleaks reads every one of them straight off navigator.
NAV_PRUNE …
```

**这直接纠正了 R156**：那一轮我把 `connection` 无条件装给了**所有** profile。
对 Apple profile 这是反的 —— WebKit 从来没发布过它，它必须**不存在**。
而桌面样本确实读 `navigator.connection`。

> **同一个成员，一个 claim 装、另一个 claim 删。** 这就是本轮写进 `NavPrune.Rule` 的话。

### 一、`NavPrune`

九个名字：`userAgentData`、`getBattery`、`connection`、`bluetooth`、`usb`、`hid`、`serial`、`xr`、`deviceMemory`。

**删除而不是设陷阱** —— 因为「答否」和「不存在」不是一回事，`for in` 仍然会走到一个陷阱属性。
执行时对**实例和原型都删**；顺序在引擎块之后（否则删的是它刚装的那个）。

### 二、真浏览器两个 claim 各测一遍

```
phone   leaves = []
desktop keeps  = ["object","4g"]
```

`deviceMemory` 尤其有意思：它正是 replica 自己装的那个，现在对手机必须删掉。

### 三、`credentials` 四元组：**记录，但不实现**

```
get                  length 1
create               length 1
preventSilentAccess  length 0
store                length 1
```

原版的 `get` 里是 `he(e,true)`、`create` 里是 `ge(e)` —— 一个**虚拟认证器**，
用来过 3DS 的 WebAuthn 挑战。这一轮只把**形状**记下来，并把「没实现」写成明文：

```csharp
public const string CredentialsOpenItem =
    "the image's credentials.get/create are a working WebAuthn shim (virtual authenticator for 3-D Secure " +
    "challenges); this workspace records the shape and has not built the authenticator";
```

### 四、这一轮的一句话

> R156 我写「`connection` 是引擎成员，对所有 profile 都装」。R163 的注释告诉我：
> **它只对桌面成立，对手机是必须删的。**
>
> **「对所有 profile」这种说法，通常是「我只验证了一个 profile」的伪装。**
'''

if "## 剪枝：同一成员" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("prune documented")
else:
    print("already present")
