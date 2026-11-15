import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 最后一层：**调用终于有人调用了**（第 142 轮）

R140 接了 Cloudflare，R141 接了 Kasada —— 两处都是**没人调用的类**。
这是同一个缺陷再下一层：**调用存在，但没有调用者。**

`DetectAsync` 是唯一知道「哪道墙挡在前面」的地方，所以它也是唯一该分派的地方。

```csharp
c.Session.Vars["antibot"] = vendor;
c.Emit($"{Name}: anti-bot = {vendor}", "detect");
return await SolveDetectedWallAsync(c, ct);
```

### 分派只覆盖审计里「已接」的两个

```csharp
if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();
```

测试 `OnlyWiredWallsAreDispatched` 与 `VendorWiring.Wired` 对得上 ——
**分派范围 = 审计说已接的范围**，两处不许各说各的。

### 没有浏览器时记录**事实**，不是失败

```csharp
if (ChromiumBridge.FindBrowser() is null) {
    c.Session.Vars["antibot.solver"] = "unavailable";
    c.Emit($"{Name}: no Chromium build, {vendor} wall left to the next attempt", "antibot");
    return StepOutcome.Success();
}
c.Session.Vars["antibot.solver"] = "available";
```

因为：in-bot 跑不起来，而服务那半没配置 —— **跑了也只会每页打一行拒绝**。
所以记 `unavailable` 让流程继续。这条能在没有浏览器的机器上被测试，所以它被测试钉住了。

### 这一轮的一句话

> 同一个缺陷我修了四轮：存储 → 调用 → 调用者 → **调用者的触发条件**。
> 每一轮它都长得像「这次真的补完了」。
>
> **「接线」不是一个动作，是一串：写端、读端、调用、触发。任何一环缺失，功能都等于不存在。**
'''

if "## 最后一层：**调用终于有人调用了**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("dispatch documented")
else:
    print("already present")
