import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareControllers.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''    /// <summary>The shopper-IP endpoint a risk check reads.</summary>
    public const string ShopperInfoIp = "ShopperInfo-IP";'''

add = '''    /// <summary>The shopper-IP endpoint a risk check reads.</summary>
    public const string ShopperInfoIp = "ShopperInfo-IP";

    // ---- R126: four the census found, each a clean name with a plausible tail
    /// <summary>Editing a line's quantity through the cart controller rather than the minicart.</summary>
    public const string CartUpdateProduct = "Cart-UpdateProduct";

    /// <summary>Showing a cart layer — the AJAX panel, not a page.</summary>
    public const string CartShowLayer = "Cart-ShowLayer";

    /// <summary>Adyen's component payment submit, the counterpart of <c>PaymentFromComponent</c>.</summary>
    public const string AdyenPaymentFromComponent = "Adyen-PaymentFromComponent";

    /// <summary>Adyen's PayPal order patch, used by the express flow's step 35.</summary>
    public const string AdyenPayPalPatchOrder = "Adyen-PayPalPatchOrder";

    /// <summary>Adyen's 3-D Secure 2 authorize, distinct from the generic authorize.</summary>
    public const string AdyenAuthorize3Ds2 = "Adyen-Authorize3DS2";'''

if anchor not in t:
    raise SystemExit("anchor missing")
t = t.replace(anchor, add, 1)

old_all = "        AdyenSaveExpressShopperDetails, ShopperInfoIp,"
new_all = ("        AdyenSaveExpressShopperDetails, ShopperInfoIp,\n"
           "        CartUpdateProduct, CartShowLayer, AdyenPaymentFromComponent,\n"
           "        AdyenPayPalPatchOrder, AdyenAuthorize3Ds2,")
if old_all not in t:
    raise SystemExit("All anchor missing")
t = t.replace(old_all, new_all, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("five controllers added from the census")
