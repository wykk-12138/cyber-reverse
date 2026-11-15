import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 110 轮。", "最后更新：第 111 轮。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:36])
        continue
    t = t.replace(old, new, 1)

anchor = "- **判据已拆成七步"
add = """- **Nike 是 16 步，不是 14（R111，IDA 实证）**：
  `d__41 StartEcomSession / 42 Authorize / 43 GetAccessToken / 44 FindVariant / 46 CreateBasket /
  48 SubmitCustomer / 49 ValidateAddress / 50 SubmitShippingAddress / 51 GetShippingMethods /
  52 SubmitShippingMethod / 53 SubmitBillingAddress / 54 BeginCheckout / 55 CheckInventory /
  56 GetShopperIp / 57 GetPaymentMethods / 58 SubmitOrder`。
  序号缺 45/47 = 编译器的 `MoveNext` 辅助方法，**不是漏步**。已固化为 `NikeSteps`。
  14→16 差的正好是 `StartEcomSession`+`BeginCheckout` 与 `Authorize`+`GetAccessToken` 两对。
- **查名字不够，要看「池子里相邻的那一段」**：60 轮里我只查过「有没有某个名字」，
  从没查过「这一段的边界在哪」—— 而整条链就躺在一段相邻字面量里。
- **判据已拆成七步"""
if anchor in t and "Nike 是 16 步" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
