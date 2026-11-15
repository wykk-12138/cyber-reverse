import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

flows = {
    "nike": ["StartEcomSession", "Authorize", "GetAccessToken", "FindVariant", "CreateBasket",
             "SubmitCustomer", "ValidateAddress", "SubmitShippingAddress", "GetShippingMethods"],
    "popmart": ["GetOrders", "StartDrawFlow", "FindDraw", "EnterDraw", "ChooseGoods",
                "FindMegaDraw", "RedeemMemberPoints", "EnterReservation"],
    "demandware-classic": ["AddToCart", "InitiateCheckout", "GenerateCSRF", "GetCheckout",
                           "SubmitBillingAddress", "SubmitConsignment", "ConfirmPayment"],
    "demandware-dual": ["StartAppFast", "StartAppSafe", "GetCartDw", "SaveSessionDw",
                        "ApplyDiscountApp", "SubmitOrderApp"],
    "collectplus": ["GetCollectPlusLocations", "SubmitCollectPlus", "SubmitDelivery",
                    "StartPayment", "GetPaymentUrl"],
    "structure-token": ["GetStructureToken", "CreateTransaction", "ProcessPayment",
                        "GetMerchantCode", "SubmitPayPal"],
    "johnlewis": ["WebHandOver", "SessionHandover", "GuestCallback", "GetStripePaymentIntent"],
}

lines = [l.split("  ", 1)[-1] for l in text.split("\n")]

for flow, names in flows.items():
    print("===", flow)
    found = 0
    for body in lines:
        if ">b__" not in body and ">g__" not in body:
            continue
        hits = [n for n in names if ("<" + n + ">") in body]
        if len(hits) >= 3:
            table = re.findall(r"<\s*(?:<\s*)?([A-Za-z][A-Za-z0-9_]*)\s*>\s*(?:b__|g__)\w*\|?(\d+)", body)
            uniq = {}
            for name, ordinal in table:
                uniq.setdefault(int(ordinal), name)
            print("   %d flow names; methods: %s" % (len(hits),
                  "  ".join("%d:%s" % (o, n) for o, n in sorted(uniq.items())[:20])))
            found += 1
            if found >= 2:
                break
    if not found:
        print("   no lambda literal names 3+ of its steps")
    print()
