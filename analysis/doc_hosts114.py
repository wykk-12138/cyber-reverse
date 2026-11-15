import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 店铺底下的第三方服务（第 114 轮）

不是店铺、但原版真的在调的服务层：

| 服务 | 主机 / 端点 | 它是什么（依据） |
|---|---|---|
| **Scheels 移动 API** | `https://mobile-api.scheels.com/v5/auth/guest`、`/v5/products/` | 与 R103 的 Frontastic hub **是两个 API** |
| **END Clothing REST** | `https://api2.endclothing.com/rest/V1` | Magento REST（`ApiHost` 属性名就在旁边） |
| **AYCD 收件箱** | `inbox-api.aycd.io/api/v1/{user/verify, tasks/mail/create, tasks/completed?group=}` | 「验证 key → 建收信任务 → 轮询完成」三步 |
| **Parallax Systems** | `api.parallaxsystems.io/{gen, holdcaptcha}` | **验证码服务**：属性名就叫 `GenEndpoint` / `HoldCaptchaEndpoint` |
| **Google Maps** | `maps/api/geocode/json?address=`、`maps/api/js?libraries=places&key=` | 邮编 → 地址、地址自动补全 |

### 三条读出来的结论

1. **Scheels 有两个 API**：`apihub.scheels.com/frontastic/action/…`（Web hub，R103）
   和 `mobile-api.scheels.com/v5`（移动端）。**一个店有 web 与 app 两套 API**，
   和 R112 里 Demandware 那套 `App`/`Dw` 双路步表是同一种形状。
2. **Parallax 是「占位 + 求解」两段式**：`/holdcaptcha` 先把一个验证码槽位占住，再去 `/gen`。
   这就是为什么它的属性名是两个而不是一个 —— **占位和生成是两次调用**。
3. **AYCD 的三个端点正好是设置页那三个动作**：`user/verify`（填 key 后验证）、
   `tasks/mail/create`（建任务）、`tasks/completed?group=`（按组轮询）。
   GUI 那边的 IMAP 设置页是这三个端点的界面 —— **GUI 在这里只是给端点做注脚**。

> 注：本表的总数由五个分组分别计数后相加得出，**不是手写的总数**
> （手写总数在这一轮错了一次：写 14，实际 13）。
'''

if "## 店铺底下的第三方服务" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("service hosts documented")
else:
    print("already present")
