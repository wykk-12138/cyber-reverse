import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 125 轮。", "最后更新：第 126 轮。", 1)

anchor = "- **第六个流程：Adyen/PayPal 快捷结账（R125）**"
add = (
    "- **控制器族普查（R126）**：词表现在 **33 条**，本轮新增 `Cart-UpdateProduct`、`Cart-ShowLayer`、\n"
    "  `Adyen-PaymentFromComponent`、`Adyen-PayPalPatchOrder`、`Adyen-Authorize3DS2`。\n"
    "  **第三次同型遗漏**（R117 / R125 / R126）—— 「表是窗口读出来的」是方法问题。\n"
    "- **池子会「粘」字**：裸扫得 94 个候选，大量是粘连变体（`Cart-AddProducton`、\n"
    "  `Cart-MiniCartSh92000052on`），真实数近 33。过滤规则是判断不是测量，已标成判断。\n"
    "- **第 5 次手写答案**：`Assert.Equal(\"CheckoutServices\", families[0].Key)` 凭记忆指定最大的族 ——\n"
    "  改成「最大者确实最大 + 三个必含族」的结构化断言。\n"
)

if anchor in t and "控制器族普查" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
