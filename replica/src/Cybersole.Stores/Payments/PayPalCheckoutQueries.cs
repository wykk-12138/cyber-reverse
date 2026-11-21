using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The PayPal partner checkout pair — <c>PayWithQuery</c> and <c>ShipToQuery</c> — read out of the image.
///
/// <para>
/// <b>Observed</b> (R1343): one sender, <c>sub_14110D030</c> (1512 bytes), references both documents and posts
/// them to the partner base <c>https://www.paypal.com/graphql/</c> (0x147097E78) with the envelope
/// <c>operationName</c> / <c>query</c> / <c>variables</c>. The documents are 12561 characters at 0x14712190C and
/// 2031 at 0x147139B2C; they declare <c>$token</c>, <c>$experiences</c> and <c>$withSplitTender</c>, and
/// <c>$token</c> alone.
/// </para>
///
/// <para>
/// <b>Observed:</b> the sender writes the middle variable key as <c>expeirences</c> — the same spelling the
/// currency sender uses — while the document declares <c>$experiences</c>. A faithful replica sends it the same
/// way; a test pins the pairing so nobody tidies it.
/// </para>
///
/// <para>
/// <b>Not used here:</b> a second sender, <c>sub_140F4C550</c> (2099 bytes), posts <c>PayWithQuery</c> through the
/// browser-facing checkout web with <c>checkoutuinodeweb_hermione</c>, <c>x-paypal-internal-euat</c> and
/// <c>paypal-client-metadata-id</c>. Two transports, one query; which a run wants is not established, so this
/// class implements the partner one that the other four operations share.
/// </para>
/// </summary>
public static class PayPalCheckoutQueries
{
    /// <summary>The partner base, shared with the approval and the currency conversion, 0x147097E78.</summary>
    public const string BaseUrl = PayPalPartnerApprove.BaseUrl;

    /// <summary>The pay-with operation, 0x146E3ACC0.</summary>
    public const string PayWithOperation = "PayWithQuery";

    /// <summary>The ship-to operation, 0x146E8A680.</summary>
    public const string ShipToOperation = "ShipToQuery";

    /// <summary>The pay-with endpoint: base plus operation name.</summary>
    public const string PayWithUrl = BaseUrl + PayWithOperation;

    /// <summary>The ship-to endpoint: base plus operation name.</summary>
    public const string ShipToUrl = BaseUrl + ShipToOperation;

    /// <summary>The pay-with document, 12561 characters from 0x14712190C.</summary>
    public const string PayWithDocument =
        "query PayWithQuery($token: String!, $experiences: [ThreeDSPaymentExperience], $withSplitTender: Boolean = false) {\n  checkoutSession(token: $token) {\n    declinedInstruments {\n      ...DeclinedInstrumentFragment\n      __typename\n    }\n    disallowedInstruments {\n      ...DisallowedInstrumentFragment\n      __typename\n    }\n    fundingOptions(returnAllPlans: true, groupSourcesOnType: INCENTIVE) {\n      ...FundingOptionFragment\n      __typename\n    }\n    splitFundingOptions @include(if: $withSplitTender) {\n      ...SplitFundingOptionsFragment\n      __typename\n    }\n    cart {\n      intent\n      amounts {\n        total {\n          currencyValue\n          currencyFormat\n          currencyCode\n          currencyFormatSymbolISOCurrency\n          __typename\n        }\n        __typename\n      }\n      category\n      billingChargePattern\n      __typename\n    }\n    flags {\n      allowAddresslessAddCard\n      is3DSecureRequired\n      isIncentivePresent\n      isPadPreferred\n      hasPPCreditInstallments\n      isCreditSecondButton\n      showPPCreditOffer\n      hideCart\n      showRemittanceDisclosure\n      __typename\n    }\n    paymentContingencies {\n      ...PaymentContingenciesFragment\n      __typename\n    }\n    creditFinancingOption {\n      ...CreditFinancingOptionFragment\n      __typename\n    }\n    userAction\n    checkoutSessionType\n    merchant {\n      country\n      isGambling\n      isTrustedBeneficiary\n      __typename\n    }\n    secureCustomerAuthenticationContext {\n      status\n      exemptReason\n      __typename\n    }\n    buyer {\n      userId\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment DeclinedInstrumentFragment on DeclinedInstrument {\n  id\n  declineType\n  normalizedProcessorResponse\n  lastDigits\n  type\n  name\n  issuerProductDescription\n  partialFpan\n  image {\n    url {\n      href\n      __typename\n    }\n    width\n    height\n    __typename\n  }\n  __typename\n}\n\nfragment DisallowedInstrumentFragment on DisallowedInstrument {\n  id\n  reason\n  lastDigits\n  isPreferred\n  type\n  name\n  label\n  formattedType\n  instrumentSubType\n  image {\n    url {\n      href\n      __typename\n    }\n    width\n    height\n    __typename\n  }\n  __typename\n}\n\nfragment FundingOptionFragment on FundingOption {\n  id\n  availableAmount {\n    currencyCode\n    currencyValue\n    currencyFormatSymbolISOCurrency\n    currencyFormat\n    __typename\n  }\n  fundingInstrument {\n    id\n    name\n    nameDescription\n    label\n    issuerProductDescription\n    type\n    instrumentSubType\n    lastDigits\n    image {\n      url {\n        href\n        __typename\n      }\n      width\n      height\n      __typename\n    }\n    placeholderImage: image(size: S) {\n      url {\n        href\n        __typename\n      }\n      width\n      height\n      __typename\n    }\n    largeImage: image(size: XL) {\n      url {\n        href\n        __typename\n      }\n      width\n      height\n      __typename\n    }\n    institutionImages(category: BRAND) {\n      url {\n        href\n        __typename\n      }\n      width\n      height\n      __typename\n    }\n    isPreferred\n    attribution\n    attributionDetails {\n      compactDescription\n      shortDescription\n      __typename\n    }\n    ...RewardsFragment\n    creditFields {\n      creditOffer {\n        presentmentType\n        product\n        offerCategory\n        creditOfferType\n        financingCode\n        crcOfferId\n        crossCurrencyInfo {\n          ...CrossCurrencyInfoFragment\n          __typename\n        }\n        uiElements {\n          ...CreditUIElementsFragment\n          __typename\n        }\n        creditPayLater {\n          ...CreditPayLaterFragment\n          __typename\n        }\n        __typename\n      }\n      repaymentInstrument {\n        id\n        name\n        type\n        instrumentSubType\n        lastDigits\n        __typename\n      }\n      __typename\n    }\n    payerDisclaimer\n    cryptocurrencyHoldingDetails {\n      symbol\n      quantity\n      __typename\n    }\n    __typename\n  }\n  allPlans {\n    id\n    fundingSources {\n      fundingInstrument {\n        id\n        name\n        type\n        instrumentSubType\n        lastDigits\n        ...InstallmentsFragment\n        __typename\n      }\n      fundingMethodType\n      delayedPaymentDate {\n        dateShort\n        d\n        y\n        M\n        __typename\n      }\n      amount {\n        currencyCode\n        currencyFormat\n        currencyFormatSymbolISOCurrency\n        currencySymbol\n        currencyValue\n        __typename\n      }\n      groupedSources {\n        fundingInstrument {\n          id\n          name\n          type\n          label\n          __typename\n        }\n        amount {\n          currencyCode\n          currencyFormat\n          currencySymbol\n          currencyValue\n          __typename\n        }\n        incentives {\n          id\n          balanceType\n          shortTitle\n          maxDiscount {\n            currencyCode\n            currencyValue\n            currencyFormat\n            __typename\n          }\n          type\n          percentOff\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    isSelected\n    backupFundingInstrument {\n      id\n      name\n      lastDigits\n      __typename\n    }\n    currencyConversion {\n      type\n      isReadOnly\n      from {\n        currencyValue\n        currencyFormatSymbolISOCurrency\n        currencyCode\n        __typename\n      }\n      to {\n        currencyValue\n        currencyFormatSymbolISOCurrency\n        currencyCode\n        __typename\n      }\n      convertedAmount {\n        currencyValue\n        currencyFormatSymbolISOCurrency\n        currencyCode\n        currencyFormat\n        __typename\n      }\n      rateFormatted\n      __typename\n    }\n    preAuthorizationData {\n      authType\n      amount {\n        currencyFormat\n        currencyFormatSymbolISOCurrency\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment RewardsFragment on FundingInstrument {\n  rewards {\n    id\n    relatedCardId\n    rewardType\n    availableRewards {\n      value\n      denominationTypeDescription\n      monetaryValue {\n        currencySymbol\n        currencyValue\n        currencyCode\n        currencyFormat\n        __typename\n      }\n      __typename\n    }\n    conversionMetadata {\n      conversionFactor\n      decimalPrecision {\n        toAmount\n        toRewards\n        __typename\n      }\n      roundingMode {\n        toAmount\n        toRewards\n        __typename\n      }\n      __typename\n    }\n    constraints {\n      minimumSpend {\n        currencySymbol\n        currencyValue\n        currencyCode\n        __typename\n      }\n      maximumSpend {\n        currencySymbol\n        currencyValue\n        currencyCode\n        __typename\n      }\n      maximumUsable {\n        currencySymbol\n        currencyValue\n        currencyCode\n        __typename\n      }\n      __typename\n    }\n    balance {\n      targetCurrencyCode\n      isConvertable\n      __typename\n    }\n    issuer {\n      name\n      instrumentType\n      issuerProductDescription\n      __typename\n    }\n    redemptionType\n    termsUrl\n    image(size: S) {\n      url {\n        href\n        __typename\n      }\n      width\n      height\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CrossCurrencyInfoFragment on CreditCrossCurrency {\n  currencyConversionRate\n  fromCurrencyCode\n  fromFormattedCurrencyConversionValue\n  fxAuditTrailId\n  toCurrencyCode\n  toFormattedCurrencyConversionValue\n  rateDescriptor\n  learnMoreText\n  learnMoreLink\n  currencyConversionDescriptor\n  __typename\n}\n\nfragment CreditUIElementsFragment on CreditUIElements {\n  creditOffer {\n    sectionHeadlineText\n    headlineText\n    descriptorText\n    continueButtonText\n    __typename\n  }\n  creditOnlyFI {\n    descriptorText\n    headlineText\n    paymentFormattedText\n    termFormattedText\n    termsText\n    __typename\n  }\n  creditFI {\n    headlineText\n    descriptorText\n    payButtonText\n    continueButtonText\n    __typename\n  }\n  isMultiOffer\n  fiHighlightText\n  logoAltText\n  logo {\n    href\n    __typename\n  }\n  __typename\n}\n\nfragment CreditPayLaterFragment on CreditPayLater {\n  totalCost {\n    currencyFormat\n    __typename\n  }\n  totalFee {\n    currencyFormat\n    __typename\n  }\n  totalInterest {\n    currencyFormat\n    __typename\n  }\n  installmentsSchedule {\n    principal {\n      currencyFormat\n      __typename\n    }\n    paymentType\n    paymentNumber\n    interest {\n      currencyFormat\n      __typename\n    }\n    consumerFee {\n      currencyFormat\n      __typename\n    }\n    paymentDate\n    totalPayment {\n      currencyCode\n      currencyFormat\n      currencyFormatSymbolISOCurrency\n      currencyValue\n      currencySymbol\n      __typename\n    }\n    __typename\n  }\n  noDownPaymentAmt {\n    currencyCode\n    currencyFormat\n    currencyFormatSymbolISOCurrency\n    currencyValue\n    currencySymbol\n    __typename\n  }\n  __typename\n}\n\nfragment InstallmentsFragment on FundingInstrument {\n  installments {\n    term\n    monthlyPayment {\n      currencyCode\n      currencyFormat\n      currencyFormatSymbolISOCurrency\n      currencySymbol\n      currencyValue\n      __typename\n    }\n    totalCost {\n      currencyCode\n      currencyFormat\n      currencyFormatSymbolISOCurrency\n      currencySymbol\n      currencyValue\n      __typename\n    }\n    discount {\n      amount {\n        currencyCode\n        currencyFormat\n        currencyFormatSymbolISOCurrency\n        currencySymbol\n        currencyValue\n        __typename\n      }\n      percentage\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SplitFundingOptionsFragment on SplitFundingOptions {\n  id\n  isEligibleForPrimaryInstrument\n  canSplitWith\n  canEditAmount\n  mustUseFullAmount\n  availableAmount {\n    currencyCode\n    currencyValue\n    currencySymbol\n    __typename\n  }\n  fundingInstrument {\n    id\n    name\n    nameDescription\n    type\n    instrumentSubType\n    lastDigits\n    image {\n      url {\n        href\n        __typename\n      }\n      width\n      height\n      __typename\n    }\n    attribution\n    incentiveDetails {\n      shortTitle\n      balanceType\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PaymentContingenciesFragment on PaymentContingencies {\n  confirmCreditCardCvvData {\n    ...ConfirmCreditCardCvvFields\n    __typename\n  }\n  sepaMandateAcceptanceNeeded {\n    ...SepaMandateAcceptanceNeededFragment\n    __typename\n  }\n  threeDomainSecure(experiences: $experiences) {\n    ...ThreeDomainSecureFields\n    __typename\n  }\n  threeDSContingencyData {\n    ...ThreeDomainSecureContingencyFragment\n    __typename\n  }\n  needConsentForBankAccountInfoRetrieval {\n    encryptedId\n    __typename\n  }\n  needRealTimeBalanceForBankAccount {\n    encryptedId\n    __typename\n  }\n  strongCustomerAuthenticationRequired {\n    contextId\n    __typename\n  }\n  __typename\n}\n\nfragment ConfirmCreditCardCvvFields on ConfirmCreditCardCvvContingency {\n  encryptedId\n  lastFourDigits\n  type\n  __typename\n}\n\nfragment SepaMandateAcceptanceNeededFragment on BankAccount {\n  id\n  type\n  accountNumber\n  accountNumberShort\n  bankIdentifierCode\n  currencyCode\n  beneficiaries {\n    fullName\n    __typename\n  }\n  billingAddress {\n    city\n    country\n    state\n    fullAddress\n    __typename\n  }\n  issuer {\n    name\n    __typename\n  }\n  creditor {\n    id\n    name\n    address {\n      fullAddress\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ThreeDomainSecureFields on ThreeDomainSecureContingency {\n  redirectUrl {\n    href\n    __typename\n  }\n  status\n  method\n  parameter\n  encryptedId\n  experience\n  requestParams {\n    key\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment ThreeDomainSecureContingencyFragment on ThreeDomainSecureResolutionContingency {\n  name\n  causeName\n  resolution {\n    type\n    resolutionName\n    paymentCard {\n      id\n      type\n      number\n      encryptedNumber\n      bankIdentificationNumber\n      billingAddress {\n        line1\n        line2\n        state\n        city\n        postalCode\n        country\n        __typename\n      }\n      expireYear\n      expireMonth\n      currencyCode\n      cardProductClass\n      __typename\n    }\n    contingencyContext {\n      source\n      reason\n      referenceId\n      deviceDataCollectionUrl {\n        href\n        __typename\n      }\n      jwtSpecification {\n        jwtIssuer\n        jwtOrgUnitId\n        jwtDuration\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CreditFinancingOptionFragment on CreditFinancingOption {\n  financingCode\n  monthlyPayment\n  totalCost\n  totalInterest\n  apr\n  term\n  creditType\n  paypalSubsidy\n  monthlyPercentageRate\n  __typename\n}\n";

    /// <summary>The ship-to document, 2031 characters from 0x147139B2C.</summary>
    public const string ShipToDocument =
        "query ShipToQuery($token: String!) {\n  checkoutSession(token: $token) {\n    merchant {\n      name\n      __typename\n    }\n    shippingAddresses {\n      ...ShippingAddressesFragment\n      __typename\n    }\n    flags {\n      isChangeShippingAddressAllowed\n      hideShipping\n      blockNonDomesticShipping\n      isOptionallyShareAddress\n      isSntSupported\n      __typename\n    }\n    cart {\n      total {\n        currencyFormatSymbolISOCurrency\n        currencyCode\n        currencyValue\n        __typename\n      }\n      amounts {\n        ...ShippingCartAmountFragment\n        __typename\n      }\n      shippingMethods {\n        id\n        type\n        label\n        selected\n        amount {\n          currencyCode\n          currencyValue\n          currencyFormatSymbolISOCurrency\n          __typename\n        }\n        __typename\n      }\n      cancelUrl {\n        href\n        __typename\n      }\n      paymentId\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ShippingAddressesFragment on CheckoutShippingAddress {\n  isPrimary\n  isSelected\n  isDisabled\n  isDefault\n  state\n  postalCode\n  country\n  city\n  name {\n    fullName\n    __typename\n  }\n  fullAddress\n  addressId\n  __typename\n}\n\nfragment ShippingCartAmountFragment on CartAmounts {\n  discount {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  handlingFee {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  insurance {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  shipping {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  shippingAndHandling {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  shippingDiscount {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  subtotal {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  tax {\n    currencyCode\n    currencyValue\n    currencyFormat\n    __typename\n  }\n  total {\n    currencySymbol\n    currencyFormat\n    __typename\n  }\n  __typename\n}\n";

    /// <summary>
    /// The three variable keys the pay-with sender writes — including <c>expeirences</c>, which the document
    /// calls <c>$experiences</c>. The ship-to query declares only <c>token</c>.
    /// </summary>
    public static readonly string[] PayWithVariableNames = { "token", "withSplitTender", "expeirences" };

    /// <summary>The request body the sender builds.</summary>
    public static JObject Envelope(string operation, string document, JObject variables) => new()
    {
        ["operationName"] = operation,
        ["query"] = document,
        ["variables"] = variables,
    };

    /// <summary>Ask what the buyer can pay with. Null with a reason when the reply carries no session.</summary>
    public static async Task<(JObject? Session, string Error)> PayWithAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
        => await AskAsync(c, PayWithOperation, PayWithDocument, variables, "checkoutSession", ct,
            url ?? PayWithUrl).ConfigureAwait(false);

    /// <summary>Ask where the buyer's order ships. Same envelope, one variable.</summary>
    public static async Task<(JObject? Session, string Error)> ShipToAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
        => await AskAsync(c, ShipToOperation, ShipToDocument, variables, "checkoutSession", ct,
            url ?? ShipToUrl).ConfigureAwait(false);

    private static async Task<(JObject? Session, string Error)> AskAsync(
        FlowContext c, string operation, string document, JObject variables, string root, CancellationToken ct,
        string url)
    {
        if (variables?["token"] is null || string.IsNullOrEmpty(variables["token"]!.ToString()))
            return (null, operation + ": no token — the query is keyed by the buyer token");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url, Envelope(operation, document, variables), "paypal-checkout", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, operation + ": no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, operation + ": " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var session = reply["data"]?[root] as JObject ?? reply["data"] as JObject;
            return session is null ? (null, operation + ": no session in reply") : (session, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, operation + ": " + ex.GetType().Name);
        }
    }
}
