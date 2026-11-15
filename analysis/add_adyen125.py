import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareControllers.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>Adyen's payment-details call, used by the component-based flow.</summary>
    public const string AdyenPaymentsDetails = "Adyen-PaymentsDetails";'''

new = '''    /// <summary>Adyen's payment-details call, used by the component-based flow.</summary>
    public const string AdyenPaymentsDetails = "Adyen-PaymentsDetails";

    // ---- R125: two the payment-flow literal pinned
    /// <summary>Express-checkout shopper details — the Adyen PayPal flow's step 37.</summary>
    public const string AdyenSaveExpressShopperDetails = "Adyen-SaveExpressShopperDetails";

    /// <summary>The shopper-IP endpoint a risk check reads.</summary>
    public const string ShopperInfoIp = "ShopperInfo-IP";'''

if old not in t:
    raise SystemExit("adyen anchor missing")
t = t.replace(old, new, 1)

old_all = "        UpdateShippingMethod, Adyen3Ds2, AdyenPaymentsDetails,"
new_all = ("        UpdateShippingMethod, Adyen3Ds2, AdyenPaymentsDetails,\n"
           "        AdyenSaveExpressShopperDetails, ShopperInfoIp,")
if old_all not in t:
    raise SystemExit("All anchor missing")
t = t.replace(old_all, new_all, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("two controllers added")
