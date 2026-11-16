"""Adjudicate every name in docs/ASYNC_OPS.md that is still undecided, and write the table back. (R842)

Round 841 ran twenty-four names through a probe table by hand. The remaining thirty-nine need the same treatment, and the
script has now been used twice, so it becomes a permanent tool rather than a one-off: it reads the undecided rows out of
docs/ASYNC_OPS.md, probes each with a word list, applies the rule R841 established, and appends a verdict table.

The rule, stated once so it is not re-derived:
    0 files matched        -> undecided; the word may simply not be the one the replica uses
    1 to 5 files matched   -> candidate; the hits name files to read
    more than 5 files      -> the word carries no information. This is NOT a hit, and it is NOT an absence: it means
                              the probe failed, and the files it hit must be inspected to tell "the capability exists
                              under another name" from "the word is generic"

Reading only -- no product code is touched.
"""

import io
import os
import re
import sys

ROOT = r"D:\projects\cyber-reverse"
SRC = os.path.join(ROOT, "replica", "src")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

# name -> candidate probe words, most distinctive first
PROBES = {
    # cart-add variants
    "AddToCartAstro": ["Astro"],
    "AddToCart2": ["AddToCart2", "addSecond", "SecondAdd"],
    "AddToCartDummy": ["Dummy"],
    "AddToCartNext": ["__NEXT_DATA__", "_next/", "nextjs", "NextData"],
    # cart reads
    "CheckCart": ["CheckCart", "VerifyCart"],
    "VerifyCart": ["VerifyCart"],
    "GetCartCookie": ["CartCookie", "cartCookie"],
    "GetCartCsrf": ["CartCsrf"],
    "GetCartId": ["CartId"],
    "GetCartItemId": ["CartItemId", "LineItemId"],
    "GetCartLines": ["CartLines"],
    "GetCartPage": ["CartPage"],
    "GetCartValue": ["CartValue"],
    "GetCartValueApp": ["CartValueApp", "CartValue"],
    "ShopAddToCart": ["ShopAddToCart"],
    # checkout face still open
    "StartCheckout": ["StartCheckout", "InitiateCheckout"],
    "StartCheckoutAstro": ["StartCheckout"],
    "StartInvoiceCheckout": ["InvoiceCheckout", "Invoice"],
    "GetCheckoutHtml": ["CheckoutHtml"],
    "GetCheckoutPage": ["CheckoutPage"],
    "GetSweepStakeCheckout": ["SweepStake"],
    "PreloadCheckout": ["PreloadCheckout"],
    "CompleteOrder": ["CompleteOrder"],
    "HandleOrderResult": ["OrderResult"],
    "RpcCreateOrder": ["RpcCreateOrder", "CreateOrder"],
    # raffle and tasks
    "RaffleOrder": ["RaffleOrder", "Raffle"],
    "StartPopNowViewTask": ["PopNow"],
    "StartDailyCheckInTask": ["DailyCheckIn", "CheckIn"],
    # task framework
    "FetchTasks": ["FetchTasks"],
    "SetupTask": ["SetupTask"],
    "StartTasksFlow": ["TasksFlow", "StartTasks"],
    "Login_EnsureTaskAlive": ["EnsureTaskAlive", "KeepAlive"],
    "StartSignupFlow": ["SignupFlow", "Signup"],
    "LoadGuestSignup": ["GuestSignup"],
    "GetRegisterSession": ["RegisterSession", "Registration"],
    # other
    "CheckPreOrderState": ["PreOrder"],
    "DetectByteOrderMarkAsync": ["ByteOrderMark"],
    "StepByteOrderMarkAsync": ["ByteOrderMark"],
    "_TryReturnTask": ["TryReturn"],
}

sources = []
for d, _, fs in os.walk(SRC):
    for f in fs:
        if f.endswith(".cs"):
            p = os.path.join(d, f)
            sources.append((f, io.open(p, encoding="utf-8", errors="replace").read()))


def probe(word):
    return [(f, t.count(word)) for f, t in sources if word in t]


rows = []
for name in sorted(PROBES):
    verdict, detail = "待判", ""
    for w in PROBES[name]:
        hits = probe(w)
        n = len(hits)
        if n == 0:
            detail = "`%s` 0 文件" % w
            continue
        if n > 5:
            sample = ", ".join(f for f, _ in hits[:4])
            detail = "`%s` %d 文件（%s …）—— 探针无辨识力，**命中文件需人工判**" % (w, n, sample)
            verdict = "探针无辨识力"
            break
        detail = "`%s` -> %s" % (w, ", ".join("%s x%d" % (f, c) for f, c in hits[:3]))
        verdict = "改名实现"
        break
    rows.append((name, verdict, detail))

print("  %-28s %-16s %s" % ("name", "verdict", "evidence"))
for n, v, d in rows:
    print("  %-28s %-16s %s" % (n, v, d[:74]))

counts = {}
for _, v, _ in rows:
    counts[v] = counts.get(v, 0) + 1
print()
print("  totals: %s" % counts)

block = "\n### 第三批（R842）：其余 %d 条\n\n" % len(rows)
block += "| 名字 | 裁决 | 依据 |\n|---|---|---|\n"
for n, v, d in rows:
    block += "| `%s` | %s | %s |\n" % (n, v, d)
block += "\n**合计**：%s\n" % counts
block += ("\n**「探针无辨识力」不是裁决** —— 它只说这个词太常见。\n"
          "**那些命中文件必须人工看：它们是关于这件事的（能力存在）还是无关的（词没用）。**\n")

if "第三批（R842）" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write(block)
    print("  ASYNC_OPS.md: batch 3 appended")
else:
    print("  ASYNC_OPS.md already has batch 3")
