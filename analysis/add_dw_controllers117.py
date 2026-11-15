import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareControllers.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    // ---- payment
    public const string AdyenAuthorize = "AdyenUpgrade-Authorize";'''

new = '''    // ---- payment
    public const string AdyenAuthorize = "AdyenUpgrade-Authorize";

    // ---- R117: five more the R94 window missed, plus the Adyen component family
    /// <summary>The billing-address submit — the step list's <c>SubmitBillingAddress</c>.</summary>
    public const string SubmitBilling = "CheckoutServices-SubmitBilling";

    /// <summary>Two-phase payment: this is the confirmation after the submit.</summary>
    public const string PaymentAuthorization = "CheckoutServices-PaymentAuthorization";

    /// <summary>Fetches the checkout's order model — what a "get checkout" really returns.</summary>
    public const string FetchOrderModel = "CheckoutServices-FetchOrderModel";

    /// <summary>Cash-on-delivery submit, the one non-card path.</summary>
    public const string SubmitCash = "CheckoutServices-SubmitCash";

    /// <summary>Changing the shipping method after the consignment exists.</summary>
    public const string UpdateShippingMethod = "CheckoutShippingServices-UpdateShippingMethod";

    /// <summary>Adyen's 3-D Secure 2 hand-off.</summary>
    public const string Adyen3Ds2 = "Adyen-Adyen3DS2";

    /// <summary>Adyen's payment-details call, used by the component-based flow.</summary>
    public const string AdyenPaymentsDetails = "Adyen-PaymentsDetails";'''

if old not in t:
    raise SystemExit("payment anchor missing")
t = t.replace(old, new, 1)

old_all = "        AdyenAuthorize, SaleSignupSubmit, SaleConfig,"
new_all = ("        AdyenAuthorize, SaleSignupSubmit, SaleConfig,\n"
           "        SubmitBilling, PaymentAuthorization, FetchOrderModel, SubmitCash,\n"
           "        UpdateShippingMethod, Adyen3Ds2, AdyenPaymentsDetails,")
if old_all not in t:
    raise SystemExit("All anchor missing")
t = t.replace(old_all, new_all, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("six controller names added (billing, authorization, order model, cash, shipping update, adyen)")
