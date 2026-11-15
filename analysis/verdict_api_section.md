### 远程 Store 名单：认证机制找到了，路径没拿到

`Store` 名单是服务器下发的（二进制里搜 `Zadoys` / `Zaibatsu` / `Buttercup Lynne`
全部 0 命中）。一直记为"无法静态枚举"。这轮试了它的 API。

### 从二进制挖出的完整主机清单

```
https://api.cybersole.io                       主 API
https://cybersole.io/api/apisecuretoken        匿名 token
https://cf-solver.cybersole.io                 Cloudflare solver
https://telemetry.cybersole.io                 遥测
https://analytics.cybersole.io                 分析
https://match.cybersole.io                     匹配服务
https://cdn.cybersole.io/releases/             更新源
https://inbox-api.aycd.io/api/v1/tasks/mail/create    AYCD 邮箱
https://inbox-api.aycd.io/api/v1/tasks/completed?group=
https://inbox-api.aycd.io/api/v1/user/verify
```

### 匿名 token 能拿到

```
GET https://cybersole.io/api/apisecuretoken
-> 200 {"token":"Mcmi2Yad06z1wlA4.TnXoFTYwXPVLq2AU…=="}
```

**不需要任何认证**。这是个匿名会话 token。

### 但 API 路径猜不中

用这个 token 试了六条路径：

```
/api/stores     404
/api/v1/stores  404
/api/modules    404
/api/v1/modules 404
/stores         404
/api/store      404
```

回二进制里找路径片段，**只有主机名，没有任何路径字符串**：

```
https://api.cybersole.io      <- 到主机为止
```

**说明路径是运行时拼的**——可能是 `base + "/" + verb` 或者走了别的机制
（gRPC？protobuf？自定义协议？）。

### 所以这条线也停在这

| 项 | 状态 |
|---|---|
| API 主机 | ✅ 全部找到 |
| 匿名 token | ✅ 能拿到，无需认证 |
| API 路径 | ❌ 二进制里没有，猜了六个都不是 |
| Store 名单 | ❌ 仍未拿到 |

**要往下走需要一次抓包**：打开 Cybersole → 进 Tasks → Create Group → 点 Store 下拉，
用 `NetworkCapture` 记录它请求了什么。

**但**：`api.cybersole.io` 不经过浏览器，`NetworkCapture` 抓不到。
需要的是 **HTTP 代理拦截**或者 **Fiddler 那种抓包**——工具链里没有。

### 一个观察

这轮和 BSTN 那五轮有个共同点：**都卡在"看不到实际请求"**。

- BSTN：商品链接不在 DOM 里，要么点要么拦网络
- Cybersole API：请求不走浏览器，要么代理要么反编译拼接逻辑

**两者缺的是同一类工具：能看到任意进程网络流量的能力。**

现在有的是"能看浏览器流量"（CDP）和"能看自己发的请求"（NetClient）。
缺的是中间那层。

---
