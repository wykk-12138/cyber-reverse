using System.Net.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// PayPal 3-D Secure — the challenge layer a PayPal payment runs when the bank asks for it,
/// decompiled end to end across R1078–R1086.
///
/// <para>
/// <b>The request template</b> (every stage, both dialects — sub_141102970 normal /
/// sub_141105A80 hosted, and the nine builders' twins): a PUT to the frozen
/// <c>https://www.paypal.com/graphql/</c> literal (0x147097e78, send step sub_14110D670) with a
/// thirty-second budget (+236 = 30000), a white <c>StatusInfo</c> wall, and the dispatch
/// <b>200 → success continuation, 403 and 429 → one shared retry closure</b>. The headers are
/// PayPal's own web-client fingerprint — <c>x-app-name: checkoutuinodeweb_hermione</c>
/// (0x146fc7338), <c>x-paypal-internal-euat</c>, <c>paypal-client-metadata-id</c>, the
/// sec-fetch family on the normal dialect, <c>x-requested-with</c>/<c>x-locale</c>/
/// <c>x-country</c>/<c>priority</c> on the hosted one.
/// </para>
///
/// <para>
/// <b>The payloads are persisted graphql operations</b> (R1083/R1085): each request body is
/// <c>{"operationName": N, "variables": {...}}</c> — the queries live server-side and are
/// referenced by name. The machine drives, in order: the contingency read (the submit stage),
/// <c>GetThreeDsJwtQuery</c>, the challenge window, <c>ThreeDsAuthenticateMutation</c>,
/// <c>ThreeDsLookUpMutation</c>, and <c>ResolveThreeDsContingency</c> with the six variables
/// token / authId / referenceId / creditCardId / status / experiences.
/// </para>
///
/// <para>
/// <b>The challenge window</b> (R1084/R1085): the response's contingency carries the bank's
/// redirect; the original opens a <c>500x600</c> window whose page is the frozen
/// <c>https://www.paypal.com/checkoutweb/processThreedsConfirmation</c> (0x147097d08), and the
/// window's post-back form carries exactly two fields, <c>JWT</c> (0x146dd3a08) and
/// <c>MD</c> (0x146df88d0). The resolver variables are read back through both a JSON needle
/// (<c>"referenceId":"</c>, via sub_140940820 / sub_140D91B40) and the challenge page's hidden
/// input (<c>input[id='referenceId']</c>, via sub_14092F630) — two sources, one value.
/// </para>
///
/// <para>
/// The four machine states the image names — <c>Submit3DS · Process3DS · Waiting3DS ·
/// Complete3DS</c> — map onto this class as: <see cref="RunAsync"/> (submit + contingency read +
/// JWT query, stopping at the window because the window is host-driven), and
/// <see cref="ContinueAsync"/> (authenticate + lookup + resolve once the window answered).
/// </para>
/// </summary>
public sealed class PayPalThreeDs
{
    /// <summary>The stage target, a frozen literal (0x147097e78): PayPal's own graphql surface.</summary>
    public const string GraphqlUrl = "https://www.paypal.com/graphql/";

    /// <summary>PayPal's web client id (0x146fc7338) — hermione is its checkout UI node's own name.</summary>
    public const string AppName = "checkoutuinodeweb_hermione";

    /// <summary>
    /// Stage 1's wall text (0x146e93fa8 = chars 0x146e93fb4 - 12). R1081 correction: the frozen
    /// literal carries the stage suffix — an earlier version read the doc's shorthand without the
    /// "(1)" and pinned that; the pool listing was the authority all along.
    /// </summary>
    public const string SolvingStatus = "Solving PayPal 3DS (1)";

    /// <summary>Stage text when the challenge flag is on (0x146e4a918) — the image's own spelling, kept.</summary>
    public const string ProcessingStatus = "Proccesing 3D Secure";

    /// <summary>The budget both builders pin (+236), in milliseconds.</summary>
    public const int StageTimeoutMs = 30000;

    /// <summary>The challenge window's page, a frozen literal (0x147097d08).</summary>
    public const string ChallengeWindowUrl = "https://www.paypal.com/checkoutweb/processThreedsConfirmation";

    /// <summary>The challenge window's width, from the frozen <c>_500_x_600</c> size (0x146f5ff08).</summary>
    public const int ChallengeWindowWidth = 500;

    /// <summary>The challenge window's height.</summary>
    public const int ChallengeWindowHeight = 600;

    /// <summary>The window's first post-back field (0x146dd3a08).</summary>
    public const string JwtFormField = "JWT";

    /// <summary>The window's second post-back field (0x146df88d0).</summary>
    public const string MdFormField = "MD";

    /// <summary>The graphql persisted-operation names, decoded from the solver bodies.</summary>
    public const string JwtQueryOperation = "GetThreeDsJwtQuery";               // 0x146da0cf0
    public const string AuthenticateOperation = "ThreeDsAuthenticateMutation"; // 0x146eef8a0
    public const string LookUpOperation = "ThreeDsLookUpMutation";             // 0x146eef8f0
    public const string ResolveOperation = "ResolveThreeDsContingency";         // the six-variable resolver

    /// <summary>The resolver's status values, carried in the <c>status</c> variable.</summary>
    public const string ResolveStatusSucceeded = "SUCCESS";
    public const string ResolveStatusFailed = "FAILED";

    /// <summary>The GetThreeDsJwtQuery document, verbatim (630 chars) - obj 0x1471213F8.</summary>
    public const string JwtQueryDocument = @"query GetThreeDsJwtQuery($referenceId: String!, $cardBin: String, $jwtIssuer: String!, $jwtOrgUnitId: String!, $returnUrl: String, $redirectUrl: String, $transactionId: String, $paymentAuthenticationRequest: String, $authenticationProvider: String, $cardType: String) {
  threeDSJwt(
    referenceId: $referenceId
    cardBin: $cardBin
    jwtIssuer: $jwtIssuer
    jwtOrgUnitId: $jwtOrgUnitId
    returnUrl: $returnUrl
    redirectUrl: $redirectUrl
    transactionId: $transactionId
    paymentAuthenticationRequest: $paymentAuthenticationRequest
    authenticationProvider: $authenticationProvider
    cardType: $cardType
  )
}
";

    /// <summary>The ThreeDsAuthenticateMutation document, verbatim (813 chars) - obj 0x1470E1FA0.</summary>
    public const string AuthenticateDocument = @"mutation ThreeDsAuthenticateMutation($token: String, $amount: AmountInput!, $productDetails: ProductDetails, $threeDsServerTransactionId: String!, $paymentAuthenticationRequest: String!, $authenticatePayload: threedsLookUpPayload!) {
  threeDSAuthenticate(
    token: $token
    amount: $amount
    productDetails: $productDetails
    authenticatePayload: $authenticatePayload
    threeDsServerTransactionId: $threeDsServerTransactionId
    paymentAuthenticationRequest: $paymentAuthenticationRequest
  ) {
    cavv
    threeDSStatus
    threeDSVersion
    liabilityShift
    enrollmentStatus
    cardBrandProcessed
    threeDSUcafIndicator
    threeDSTransactionId
    threeDSEcommerceIndicator
    signatureVerificationStatus
    authenticationThreeDSStatus
    threeDsAuthenticationReason
    __typename
  }
}
";

    /// <summary>The ThreeDsLookUpMutation document, verbatim (871 chars) - obj 0x1470E2CC0.</summary>
    public const string LookUpDocument = @"mutation ThreeDsLookUpMutation($token: String!, $amount: AmountInput!, $productDetails: ProductDetails, $browserInfo: ThreedsBrowserDetailsInput, $threedsLookUpPayload: threedsLookUpPayload!) {
  threeDSLookUp(
    token: $token
    amount: $amount
    productDetails: $productDetails
    browserInfo: $browserInfo
    threedsLookUpPayload: $threedsLookUpPayload
  ) {
    acsURL {
      href
      __typename
    }
    redirectURL {
      href
      __typename
    }
    cavv
    threeDSStatus
    transactionId
    liabilityShift
    enrollmentStatus
    cardBrandProcessed
    threeDSUcafIndicator
    threeDSEcommerceIndicator
    threeDsServerTransactionId
    threeDsProcessorTraceNumber
    authenticationThreeDSStatus
    signatureVerificationStatus
    threeDsAuthenticationReason
    paymentAuthenticationRequest
    authenticationProvider
    __typename
  }
}
";

    /// <summary>The ResolveThreeDsContingency document, verbatim (10370 chars) - obj 0x1470DC9B0.</summary>
    public const string ResolveDocument = @"mutation ResolveThreeDsContingency($token: String!, $authId: String!, $referenceId: String!, $creditCardId: String!, $status: ResolveThreeDsContingencyStatus!, $experiences: [ThreeDSPaymentExperience]) {
  resolveThreeDsContingency(
    token: $token
    authId: $authId
    status: $status
    referenceId: $referenceId
    creditCardId: $creditCardId
  ) {
    state
    flags {
      is3DSecureRequired
      __typename
    }
    paymentContingencies {
      ...PaymentContingenciesFragment
      __typename
    }
    fundingOptions(returnAllPlans: true, groupSourcesOnType: INCENTIVE) {
      ...FundingOptionFragment
      __typename
    }
    __typename
  }
}

fragment PaymentContingenciesFragment on PaymentContingencies {
  confirmCreditCardCvvData {
    ...ConfirmCreditCardCvvFields
    __typename
  }
  sepaMandateAcceptanceNeeded {
    ...SepaMandateAcceptanceNeededFragment
    __typename
  }
  threeDomainSecure(experiences: $experiences) {
    ...ThreeDomainSecureFields
    __typename
  }
  threeDSContingencyData {
    ...ThreeDomainSecureContingencyFragment
    __typename
  }
  needConsentForBankAccountInfoRetrieval {
    encryptedId
    __typename
  }
  needRealTimeBalanceForBankAccount {
    encryptedId
    __typename
  }
  strongCustomerAuthenticationRequired {
    contextId
    __typename
  }
  __typename
}

fragment ConfirmCreditCardCvvFields on ConfirmCreditCardCvvContingency {
  encryptedId
  lastFourDigits
  type
  __typename
}

fragment SepaMandateAcceptanceNeededFragment on BankAccount {
  id
  type
  accountNumber
  accountNumberShort
  bankIdentifierCode
  currencyCode
  beneficiaries {
    fullName
    __typename
  }
  billingAddress {
    city
    country
    state
    fullAddress
    __typename
  }
  issuer {
    name
    __typename
  }
  creditor {
    id
    name
    address {
      fullAddress
      __typename
    }
    __typename
  }
  __typename
}

fragment ThreeDomainSecureFields on ThreeDomainSecureContingency {
  redirectUrl {
    href
    __typename
  }
  status
  method
  parameter
  encryptedId
  experience
  requestParams {
    key
    value
    __typename
  }
  __typename
}

fragment ThreeDomainSecureContingencyFragment on ThreeDomainSecureResolutionContingency {
  name
  causeName
  resolution {
    type
    resolutionName
    paymentCard {
      id
      type
      number
      encryptedNumber
      bankIdentificationNumber
      billingAddress {
        line1
        line2
        state
        city
        postalCode
        country
        __typename
      }
      expireYear
      expireMonth
      currencyCode
      cardProductClass
      __typename
    }
    contingencyContext {
      source
      reason
      referenceId
      deviceDataCollectionUrl {
        href
        __typename
      }
      jwtSpecification {
        jwtIssuer
        jwtOrgUnitId
        jwtDuration
        __typename
      }
      authenticationProvider
      cardBrandProcessed
      dataOnlyIndicator
      deviceDataCollectionBin
      __typename
    }
    __typename
  }
  __typename
}

fragment FundingOptionFragment on FundingOption {
  id
  availableAmount {
    currencyCode
    currencyValue
    currencyFormatSymbolISOCurrency
    currencyFormat
    __typename
  }
  fundingInstrument {
    id
    name
    nameDescription
    label
    issuerProductDescription
    type
    instrumentSubType
    lastDigits
    image {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    placeholderImage: image(size: S) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    largeImage: image(size: XL) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    institutionImages(category: BRAND) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    isPreferred
    attribution
    attributionDetails {
      compactDescription
      shortDescription
      __typename
    }
    ...RewardsFragment
    creditFields {
      creditOffer {
        presentmentType
        product
        offerCategory
        creditOfferType
        financingCode
        crcOfferId
        crossCurrencyInfo {
          ...CrossCurrencyInfoFragment
          __typename
        }
        uiElements {
          ...CreditUIElementsFragment
          __typename
        }
        creditPayLater {
          ...CreditPayLaterFragment
          __typename
        }
        __typename
      }
      repaymentInstrument {
        id
        name
        type
        instrumentSubType
        lastDigits
        __typename
      }
      __typename
    }
    payerDisclaimer
    cryptocurrencyHoldingDetails {
      symbol
      quantity
      __typename
    }
    __typename
  }
  allPlans {
    id
    fundingSources {
      fundingInstrument {
        id
        name
        type
        instrumentSubType
        lastDigits
        ...InstallmentsFragment
        __typename
      }
      fundingMethodType
      delayedPaymentDate {
        dateShort
        d
        y
        M
        __typename
      }
      amount {
        currencyCode
        currencyFormat
        currencyFormatSymbolISOCurrency
        currencySymbol
        currencyValue
        __typename
      }
      groupedSources {
        fundingInstrument {
          id
          name
          type
          label
          __typename
        }
        amount {
          currencyCode
          currencyFormat
          currencySymbol
          currencyValue
          __typename
        }
        incentives {
          id
          balanceType
          shortTitle
          maxDiscount {
            currencyCode
            currencyValue
            currencyFormat
            __typename
          }
          type
          percentOff
          __typename
        }
        __typename
      }
      __typename
    }
    isSelected
    backupFundingInstrument {
      id
      name
      lastDigits
      __typename
    }
    currencyConversion {
      type
      isReadOnly
      from {
        currencyValue
        currencyFormatSymbolISOCurrency
        currencyCode
        __typename
      }
      to {
        currencyValue
        currencyFormatSymbolISOCurrency
        currencyCode
        __typename
      }
      convertedAmount {
        currencyValue
        currencyFormatSymbolISOCurrency
        currencyCode
        currencyFormat
        __typename
      }
      rateFormatted
      __typename
    }
    preAuthorizationData {
      authType
      amount {
        currencyFormat
        currencyFormatSymbolISOCurrency
        __typename
      }
      __typename
    }
    __typename
  }
  __typename
}

fragment RewardsFragment on FundingInstrument {
  rewards {
    id
    relatedCardId
    rewardType
    availableRewards {
      value
      denominationTypeDescription
      monetaryValue {
        currencySymbol
        currencyValue
        currencyCode
        currencyFormat
        __typename
      }
      __typename
    }
    conversionMetadata {
      conversionFactor
      decimalPrecision {
        toAmount
        toRewards
        __typename
      }
      roundingMode {
        toAmount
        toRewards
        __typename
      }
      __typename
    }
    constraints {
      minimumSpend {
        currencySymbol
        currencyValue
        currencyCode
        __typename
      }
      maximumSpend {
        currencySymbol
        currencyValue
        currencyCode
        __typename
      }
      maximumUsable {
        currencySymbol
        currencyValue
        currencyCode
        __typename
      }
      __typename
    }
    balance {
      targetCurrencyCode
      isConvertable
      __typename
    }
    issuer {
      name
      instrumentType
      issuerProductDescription
      __typename
    }
    redemptionType
    termsUrl
    image(size: S) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    __typename
  }
  __typename
}

fragment CrossCurrencyInfoFragment on CreditCrossCurrency {
  currencyConversionRate
  fromCurrencyCode
  fromFormattedCurrencyConversionValue
  fxAuditTrailId
  toCurrencyCode
  toFormattedCurrencyConversionValue
  rateDescriptor
  learnMoreText
  learnMoreLink
  currencyConversionDescriptor
  __typename
}

fragment CreditUIElementsFragment on CreditUIElements {
  creditOffer {
    sectionHeadlineText
    headlineText
    descriptorText
    continueButtonText
    __typename
  }
  creditOnlyFI {
    descriptorText
    headlineText
    paymentFormattedText
    termFormattedText
    termsText
    __typename
  }
  creditFI {
    headlineText
    descriptorText
    payButtonText
    continueButtonText
    __typename
  }
  isMultiOffer
  fiHighlightText
  logoAltText
  logo {
    href
    __typename
  }
  __typename
}

fragment CreditPayLaterFragment on CreditPayLater {
  totalCost {
    currencyFormat
    __typename
  }
  totalFee {
    currencyFormat
    __typename
  }
  totalInterest {
    currencyFormat
    __typename
  }
  installmentsSchedule {
    principal {
      currencyFormat
      __typename
    }
    paymentType
    paymentNumber
    interest {
      currencyFormat
      __typename
    }
    consumerFee {
      currencyFormat
      __typename
    }
    paymentDate
    totalPayment {
      currencyCode
      currencyFormat
      currencyFormatSymbolISOCurrency
      currencyValue
      currencySymbol
      __typename
    }
    __typename
  }
  noDownPaymentAmt {
    currencyCode
    currencyFormat
    currencyFormatSymbolISOCurrency
    currencyValue
    currencySymbol
    __typename
  }
  __typename
}

fragment InstallmentsFragment on FundingInstrument {
  installments {
    term
    monthlyPayment {
      currencyCode
      currencyFormat
      currencyFormatSymbolISOCurrency
      currencySymbol
      currencyValue
      __typename
    }
    totalCost {
      currencyCode
      currencyFormat
      currencyFormatSymbolISOCurrency
      currencySymbol
      currencyValue
      __typename
    }
    discount {
      amount {
        currencyCode
        currencyFormat
        currencyFormatSymbolISOCurrency
        currencySymbol
        currencyValue
        __typename
      }
      percentage
      __typename
    }
    __typename
  }
  __typename
}
";

    /// <summary>The PayPal REST hop beside the graphql surface: the method-complete notification (0x147098740).</summary>
    public const string NotifyMethodCompleteUrl =
        "https://www.paypal.com/payment-authentication/threeds/v1/notify-method-cmpl";

    /// <summary>
    /// The device-data initialisation endpoint (0x1470985e8, 68 chars) — the default target of
    /// the JWT form when the response names no <c>deviceDataCollectionUrl</c> of its own.
    /// </summary>
    public const string InitMethodUrl =
        "https://www.paypal.com/payment-authentication/threeds/v1/init-method";

    /// <summary>The method-notification form field (0x14716d3d0) — base64 of the transaction id.</summary>
    public const string ThreeDsMethodDataField = "threeDSMethodData";

    /// <summary>The transaction id the method-notification payload carries (0x14716d5f8).</summary>
    public const string ThreeDsServerTransIdField = "threeDSServerTransID";

    /// <summary>The response needles the device-data step reads (0x147003a88 → 0x1470494a8).</summary>
    public const string DeviceDataCollectionUrlField = "deviceDataCollectionUrl";

    /// <summary>
    /// The normal path's own surface (R1097) — a second PayPal 3DS dialect, the
    /// <c>heliosnext</c> family, wholly separate from the hosted path's
    /// <c>payment-authentication/threeds/v1</c> + graphql pair. Decoded from
    /// <c>sub_140d8d2b0</c> (6,310 bytes): the entry page, then the session bootstrap, then the
    /// challenge initialisation. The method pair (<c>init-method</c> / <c>notify-method-cmpl</c>)
    /// is the one surface the two dialects share.
    /// </summary>
    public const string HeliosEntryUrl =
        "https://www.paypal.com/heliosnext/threeDS?action=verify&flow=3ds&cart_id=";   // 0x1470983d8

    /// <summary>The normal path's server-data hop (0x1470982f0).</summary>
    public const string HeliosServerDataUrl =
        "https://www.paypal.com/heliosnext/api/serverData";

    /// <summary>The normal path's session hop (0x147098368).</summary>
    public const string HeliosSessionUrl =
        "https://www.paypal.com/heliosnext/api/session";

    /// <summary>The normal path's confirmation hop (0x147098258).</summary>
    public const string HeliosProcessThreedsConfirmationUrl =
        "https://www.paypal.com/heliosnext/api/processThreedsConfirmation";

    /// <summary>The challenge initialisation endpoint (0x147098540, 71 chars) — normal path only.</summary>
    public const string InitChallengeUrl =
        "https://www.paypal.com/payment-authentication/threeds/v1/init-challenge";

    /// <summary>
    /// The <b>base</b> of the challenge callback URL (0x147098688) — not a request target.
    ///
    /// <para>
    /// R1148 corrects R1147. The literal is met exactly once in the image, at line 1967 of
    /// <c>sub_141113680</c>:
    /// <c>v563 = sub_141CF6230(&amp;off_147098688, v9[9])</c>. That helper is a string builder — it
    /// allocates a builder, appends its first argument, appends its second and returns the join — so the
    /// URL is <b>concatenated with a value and handed to PayPal</b>, never posted to. So this endpoint
    /// has no request body; R1147's "payload still undecoded" was describing something that does not
    /// exist. The value it is joined with is the challenge id, and the joined result is the
    /// <c>challenge_callback_url</c> field (0x146fc54d8) that
    /// <see cref="ChallengeCallbackUrlFor"/> then appends its own query to.
    /// </para>
    ///
    /// <para>
    /// Note the <b>trailing slash</b>: it is what makes the join a path segment rather than a suffix.
    /// </para>
    /// </summary>
    public const string NotifyChallengeCompleteUrl =
        "https://www.paypal.com/payment-authentication/threeds/v1/notify-challenge-cmpl/";

    /// <summary>
    /// The callback base for one challenge: the literal above joined with the challenge id, which is the
    /// join the machine performs before handing the value to PayPal (R1148). Feed the result to
    /// <see cref="ChallengeCallbackUrlFor"/> to get the URL the solver actually visits.
    /// </summary>
    public static string ChallengeCallbackBaseFor(string challengeId) =>
        NotifyChallengeCompleteUrl + challengeId;

    /// <summary>The session hop's form field (0x146f6d9a8).</summary>
    public const string ActionField = "action";

    /// <summary>The bootstrap token field (0x147171d48) — both normal-path hops carry it.</summary>
    public const string TokenField = "token";

    /// <summary>The session hop's action literal (0x14717e4a8).</summary>
    public const string VerifyAction = "verify";

    /// <summary>The entry URL's trailing segment (0x146a7f400).</summary>
    public const string GoToNextSegment = "&go_to=next";

    /// <summary>The normal path's device blob field (0x147003b30) and its payload/user-agent pair.</summary>
    public const string DeviceInfoField = "deviceInfo";
    public const string PayloadField = "payload";
    public const string UserAgentField = "userAgent";

    /// <summary>The cart id and callback needles the normal path composes with (0x146fc1c58 / 0x146fc54d8).</summary>
    public const string CartIdField = "cart_id";
    public const string ChallengeCallbackUrlField = "challenge_callback_url";

    /// <summary>The normal path's failure line and colour (0x146e3b5f0 / 0x146a76fd0).</summary>
    public const string NormalPathFailureStatus = "Payment failed (3DS)";
    public const string NormalPathFailureColour = "#FB4961";

    /// <summary>
    /// The challenge callback's trailing query fragment (0x147163128, 47 chars) — the normal
    /// solver appends it while composing the callback URL in its string builder (site
    /// 0x140d8e6ff, the same region that references <c>challenge_callback_url</c>).
    /// </summary>
    public const string ChallengeCallbackFragment = "state=undefined&code=undefined&liability_shift=";

    /// <summary>
    /// Composes the callback URL the normal path visits after the challenge: the base, a separator,
    /// then the fragment <b>exactly as frozen</b>.
    ///
    /// <para>
    /// R1149: this used to substitute three values into the fragment. The machine does not — in
    /// <c>sub_140d8d2b0</c> the fragment is appended twice, as
    /// <c>sub_141D2B8E0(…, &amp;unk_147163134, 94)</c> and as <c>sub_141DC7B80(&amp;v216,
    /// &amp;off_147163128)</c>; 94 bytes is the whole 47-character literal, and neither branch
    /// touches it. So the URL always carries <c>state=undefined&amp;code=undefined</c>, which is
    /// what the frozen string says and what this returns.
    /// </para>
    ///
    /// <para>
    /// R1103 read the separator out of the same machine: <c>&amp;</c> (0x146a7aba8) when the base
    /// already contains <c>?</c> and <c>?</c> (0x146b27640) otherwise, decided by
    /// <c>sub_141cfa770(base, 63)</c>, so the join never double-asks.
    /// </para>
    /// </summary>
    public static string ChallengeCallbackUrlFor(string baseUrl)
    {
        var separator = baseUrl.Contains('?') ? "&" : "?";
        return baseUrl + separator + ChallengeCallbackFragment;
    }

    /// <summary>The frozen document for an operation name — the four the machine sends.</summary>
    /// <summary>
    /// The document for an operation. <paramref name="providerFields"/> selects the dialect: the image
    /// sends both a resolve and a look-up that include <c>authenticationProvider</c> and one of each that
    /// does not. The default is the longer text, which is what this method returned before the pairs were
    /// known.
    /// </summary>
    public static string DocumentFor(string operationName, bool providerFields = true) =>
        operationName switch
        {
            JwtQueryOperation => JwtQueryDocument,
            AuthenticateOperation => AuthenticateDocument,
            // R1324: the look-up has the same pair, so the flag means the same thing here.
            LookUpOperation => providerFields ? LookUpDocument : LookUpDocumentWithoutProviderFields,
            // R1323: the image sends two variants of the resolve mutation from two functions. The default is
            // the longer one, which is what this method returned before the variant was known.
            ResolveOperation => providerFields ? ResolveDocument : ResolveDocumentWithoutProviderFields,
            _ => string.Empty,
        };

    /// <summary>
    /// The other live variant of the same mutation — 10262 characters from 0x1470D7974, sent by
    /// <c>sub_14110FDB0</c> (14458 bytes). It is <see cref="ResolveDocument"/> with one field block missing:
    /// the longer document inserts <c>authenticationProvider</c>, <c>cardBrandProcessed</c>,
    /// <c>dataOnlyIndicator</c> and the device-data collection fields at offset 2890. Both documents are
    /// referenced exactly once in the image, so both code paths are live and the choice belongs to the
    /// caller rather than to this class.
    /// </summary>
    public const string ResolveDocumentWithoutProviderFields = @"mutation ResolveThreeDsContingency($token: String!, $authId: String!, $referenceId: String!, $creditCardId: String!, $status: ResolveThreeDsContingencyStatus!, $experiences: [ThreeDSPaymentExperience]) {
  resolveThreeDsContingency(
    token: $token
    authId: $authId
    status: $status
    referenceId: $referenceId
    creditCardId: $creditCardId
  ) {
    state
    flags {
      is3DSecureRequired
      __typename
    }
    paymentContingencies {
      ...PaymentContingenciesFragment
      __typename
    }
    fundingOptions(returnAllPlans: true, groupSourcesOnType: INCENTIVE) {
      ...FundingOptionFragment
      __typename
    }
    __typename
  }
}

fragment PaymentContingenciesFragment on PaymentContingencies {
  confirmCreditCardCvvData {
    ...ConfirmCreditCardCvvFields
    __typename
  }
  sepaMandateAcceptanceNeeded {
    ...SepaMandateAcceptanceNeededFragment
    __typename
  }
  threeDomainSecure(experiences: $experiences) {
    ...ThreeDomainSecureFields
    __typename
  }
  threeDSContingencyData {
    ...ThreeDomainSecureContingencyFragment
    __typename
  }
  needConsentForBankAccountInfoRetrieval {
    encryptedId
    __typename
  }
  needRealTimeBalanceForBankAccount {
    encryptedId
    __typename
  }
  strongCustomerAuthenticationRequired {
    contextId
    __typename
  }
  __typename
}

fragment ConfirmCreditCardCvvFields on ConfirmCreditCardCvvContingency {
  encryptedId
  lastFourDigits
  type
  __typename
}

fragment SepaMandateAcceptanceNeededFragment on BankAccount {
  id
  type
  accountNumber
  accountNumberShort
  bankIdentifierCode
  currencyCode
  beneficiaries {
    fullName
    __typename
  }
  billingAddress {
    city
    country
    state
    fullAddress
    __typename
  }
  issuer {
    name
    __typename
  }
  creditor {
    id
    name
    address {
      fullAddress
      __typename
    }
    __typename
  }
  __typename
}

fragment ThreeDomainSecureFields on ThreeDomainSecureContingency {
  redirectUrl {
    href
    __typename
  }
  status
  method
  parameter
  encryptedId
  experience
  requestParams {
    key
    value
    __typename
  }
  __typename
}

fragment ThreeDomainSecureContingencyFragment on ThreeDomainSecureResolutionContingency {
  name
  causeName
  resolution {
    type
    resolutionName
    paymentCard {
      id
      type
      number
      encryptedNumber
      bankIdentificationNumber
      billingAddress {
        line1
        line2
        state
        city
        postalCode
        country
        __typename
      }
      expireYear
      expireMonth
      currencyCode
      cardProductClass
      __typename
    }
    contingencyContext {
      source
      reason
      referenceId
      deviceDataCollectionUrl {
        href
        __typename
      }
      jwtSpecification {
        jwtIssuer
        jwtOrgUnitId
        jwtDuration
        __typename
      }
      __typename
    }
    __typename
  }
  __typename
}

fragment FundingOptionFragment on FundingOption {
  id
  availableAmount {
    currencyCode
    currencyValue
    currencyFormatSymbolISOCurrency
    currencyFormat
    __typename
  }
  fundingInstrument {
    id
    name
    nameDescription
    label
    issuerProductDescription
    type
    instrumentSubType
    lastDigits
    image {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    placeholderImage: image(size: S) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    largeImage: image(size: XL) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    institutionImages(category: BRAND) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    isPreferred
    attribution
    attributionDetails {
      compactDescription
      shortDescription
      __typename
    }
    ...RewardsFragment
    creditFields {
      creditOffer {
        presentmentType
        product
        offerCategory
        creditOfferType
        financingCode
        crcOfferId
        crossCurrencyInfo {
          ...CrossCurrencyInfoFragment
          __typename
        }
        uiElements {
          ...CreditUIElementsFragment
          __typename
        }
        creditPayLater {
          ...CreditPayLaterFragment
          __typename
        }
        __typename
      }
      repaymentInstrument {
        id
        name
        type
        instrumentSubType
        lastDigits
        __typename
      }
      __typename
    }
    payerDisclaimer
    cryptocurrencyHoldingDetails {
      symbol
      quantity
      __typename
    }
    __typename
  }
  allPlans {
    id
    fundingSources {
      fundingInstrument {
        id
        name
        type
        instrumentSubType
        lastDigits
        ...InstallmentsFragment
        __typename
      }
      fundingMethodType
      delayedPaymentDate {
        dateShort
        d
        y
        M
        __typename
      }
      amount {
        currencyCode
        currencyFormat
        currencyFormatSymbolISOCurrency
        currencySymbol
        currencyValue
        __typename
      }
      groupedSources {
        fundingInstrument {
          id
          name
          type
          label
          __typename
        }
        amount {
          currencyCode
          currencyFormat
          currencySymbol
          currencyValue
          __typename
        }
        incentives {
          id
          balanceType
          shortTitle
          maxDiscount {
            currencyCode
            currencyValue
            currencyFormat
            __typename
          }
          type
          percentOff
          __typename
        }
        __typename
      }
      __typename
    }
    isSelected
    backupFundingInstrument {
      id
      name
      lastDigits
      __typename
    }
    currencyConversion {
      type
      isReadOnly
      from {
        currencyValue
        currencyFormatSymbolISOCurrency
        currencyCode
        __typename
      }
      to {
        currencyValue
        currencyFormatSymbolISOCurrency
        currencyCode
        __typename
      }
      convertedAmount {
        currencyValue
        currencyFormatSymbolISOCurrency
        currencyCode
        currencyFormat
        __typename
      }
      rateFormatted
      __typename
    }
    preAuthorizationData {
      authType
      amount {
        currencyFormat
        currencyFormatSymbolISOCurrency
        __typename
      }
      __typename
    }
    __typename
  }
  __typename
}

fragment RewardsFragment on FundingInstrument {
  rewards {
    id
    relatedCardId
    rewardType
    availableRewards {
      value
      denominationTypeDescription
      monetaryValue {
        currencySymbol
        currencyValue
        currencyCode
        currencyFormat
        __typename
      }
      __typename
    }
    conversionMetadata {
      conversionFactor
      decimalPrecision {
        toAmount
        toRewards
        __typename
      }
      roundingMode {
        toAmount
        toRewards
        __typename
      }
      __typename
    }
    constraints {
      minimumSpend {
        currencySymbol
        currencyValue
        currencyCode
        __typename
      }
      maximumSpend {
        currencySymbol
        currencyValue
        currencyCode
        __typename
      }
      maximumUsable {
        currencySymbol
        currencyValue
        currencyCode
        __typename
      }
      __typename
    }
    balance {
      targetCurrencyCode
      isConvertable
      __typename
    }
    issuer {
      name
      instrumentType
      issuerProductDescription
      __typename
    }
    redemptionType
    termsUrl
    image(size: S) {
      url {
        href
        __typename
      }
      width
      height
      __typename
    }
    __typename
  }
  __typename
}

fragment CrossCurrencyInfoFragment on CreditCrossCurrency {
  currencyConversionRate
  fromCurrencyCode
  fromFormattedCurrencyConversionValue
  fxAuditTrailId
  toCurrencyCode
  toFormattedCurrencyConversionValue
  rateDescriptor
  learnMoreText
  learnMoreLink
  currencyConversionDescriptor
  __typename
}

fragment CreditUIElementsFragment on CreditUIElements {
  creditOffer {
    sectionHeadlineText
    headlineText
    descriptorText
    continueButtonText
    __typename
  }
  creditOnlyFI {
    descriptorText
    headlineText
    paymentFormattedText
    termFormattedText
    termsText
    __typename
  }
  creditFI {
    headlineText
    descriptorText
    payButtonText
    continueButtonText
    __typename
  }
  isMultiOffer
  fiHighlightText
  logoAltText
  logo {
    href
    __typename
  }
  __typename
}

fragment CreditPayLaterFragment on CreditPayLater {
  totalCost {
    currencyFormat
    __typename
  }
  totalFee {
    currencyFormat
    __typename
  }
  totalInterest {
    currencyFormat
    __typename
  }
  installmentsSchedule {
    principal {
      currencyFormat
      __typename
    }
    paymentType
    paymentNumber
    interest {
      currencyFormat
      __typename
    }
    consumerFee {
      currencyFormat
      __typename
    }
    paymentDate
    totalPayment {
      currencyCode
      currencyFormat
      currencyFormatSymbolISOCurrency
      currencyValue
      currencySymbol
      __typename
    }
    __typename
  }
  noDownPaymentAmt {
    currencyCode
    currencyFormat
    currencyFormatSymbolISOCurrency
    currencyValue
    currencySymbol
    __typename
  }
  __typename
}

fragment InstallmentsFragment on FundingInstrument {
  installments {
    term
    monthlyPayment {
      currencyCode
      currencyFormat
      currencyFormatSymbolISOCurrency
      currencySymbol
      currencyValue
      __typename
    }
    totalCost {
      currencyCode
      currencyFormat
      currencyFormatSymbolISOCurrency
      currencySymbol
      currencyValue
      __typename
    }
    discount {
      amount {
        currencyCode
        currencyFormat
        currencyFormatSymbolISOCurrency
        currencySymbol
        currencyValue
        __typename
      }
      percentage
      __typename
    }
    __typename
  }
  __typename
}
";

    /// <summary>
    /// The other live variant of the look-up mutation — 844 characters from 0x1470E261C. It is
    /// <see cref="LookUpDocument"/> minus the same <c>authenticationProvider</c> field block the resolve pair
    /// differs by (27 characters at offset 827), which is what makes the two pairs one dialect question
    /// rather than two coincidences.
    /// </summary>
    public const string LookUpDocumentWithoutProviderFields = @"mutation ThreeDsLookUpMutation($token: String!, $amount: AmountInput!, $productDetails: ProductDetails, $browserInfo: ThreedsBrowserDetailsInput, $threedsLookUpPayload: threedsLookUpPayload!) {
  threeDSLookUp(
    token: $token
    amount: $amount
    productDetails: $productDetails
    browserInfo: $browserInfo
    threedsLookUpPayload: $threedsLookUpPayload
  ) {
    acsURL {
      href
      __typename
    }
    redirectURL {
      href
      __typename
    }
    cavv
    threeDSStatus
    transactionId
    liabilityShift
    enrollmentStatus
    cardBrandProcessed
    threeDSUcafIndicator
    threeDSEcommerceIndicator
    threeDsServerTransactionId
    threeDsProcessorTraceNumber
    authenticationThreeDSStatus
    signatureVerificationStatus
    threeDsAuthenticationReason
    paymentAuthenticationRequest
    __typename
  }
}
";

    /// <summary>The four state-machine names the image carries for the 3DS challenge.</summary>
    public enum ThreeDsState { Submit3DS, Process3DS, Waiting3DS, Complete3DS }

    /// <summary>
    /// The nine observable stages' own labels, every one confirmed by decompile (R1081/R1082):
    /// the label objects are exactly the pool listing's chars-12 addresses — (1) 0x146e93fa8,
    /// (2) 0x146e93ff0, (2.1) 0x146e94038, (3) 0x146e94080, (4) 0x146e940c8, (5) 0x146e94110,
    /// (6) 0x146e94158, (7) 0x146e941a0, (8) 0x146e941e8. Each stage's builder is the same
    /// request template — same header dialects, same 30s budget, same 200/403/429 dispatch.
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> StageLabels =
        new Dictionary<string, string>
        {
            ["1"] = SolvingStatus,
            ["2"] = "Solving PayPal 3DS (2)",
            ["2.1"] = "Solving PayPal 3DS (2.1)",
            ["3"] = "Solving PayPal 3DS (3)",
            ["4"] = "Solving PayPal 3DS (4)",
            ["5"] = "Solving PayPal 3DS (5)",
            ["6"] = "Solving PayPal 3DS (6)",
            ["7"] = "Solving PayPal 3DS (7)",
            ["8"] = "Solving PayPal 3DS (8)",
        };

    /// <summary>
    /// True when this class can drive the named stage. R1086: the machine runs the stages through
    /// the shared graphql helper, so the answer is the label map itself — the map is closed at
    /// nine, and a stage outside it does not exist in the image.
    /// </summary>
    public static bool StageIsDecoded(string? stage) =>
        !string.IsNullOrEmpty(stage) && StageLabels.ContainsKey(stage);

    /// <summary>
    /// One stage request's inputs — the fields the builders read off their payment context.
    /// </summary>
    public sealed class StageInput
    {
        /// <summary>The flag at ctx+144 that selects the stage text in both builders.</summary>
        public bool ChallengeActive { get; init; }

        /// <summary>Which of the two builder twins runs — the normal or the hosted dialect.</summary>
        public bool Hosted { get; init; }

        /// <summary>x-paypal-internal-euat — the normal path reads ctx[2], the hosted ctx[3].</summary>
        public string? Euat { get; init; }

        /// <summary>paypal-client-metadata-id (ctx+24); the hosted dialect also echoes it as paypal-client-context.</summary>
        public string? MetadataId { get; init; }

        /// <summary>Hosted only: x-country (ctx[4]).</summary>
        public string? Country { get; init; }

        /// <summary>Hosted only: x-app-name comes from the context (ctx[2]) instead of the literal.</summary>
        public string? HostedAppName { get; init; }

        /// <summary>Hosted only: referer comes from the context (ctx[5]); the normal path sends the paypal origin.</summary>
        public string? HostedReferer { get; init; }

        /// <summary>The global config's user agent, both paths.</summary>
        public string? UserAgent { get; init; }

        /// <summary>sec-ch-ua, generated (sub_140f9a950).</summary>
        public string? SecChUa { get; init; }

        /// <summary>sec-ch-ua-platform, generated (sub_140f9bce0).</summary>
        public string? SecChUaPlatform { get; init; }

        /// <summary>The buyer token the resolver's <c>token</c> variable carries.</summary>
        public string? Token { get; init; }

        /// <summary>The checkout amount, formatted <c>{0:0.00}</c> (0x147193208) for the variables.</summary>
        public decimal Amount { get; init; }
    }

    /// <summary>
    /// What the contingency read found in the submit response — the fields the case bodies'
    /// needles pull out of <c>paymentContingencies</c> (jwtSpecification / referenceId / the
    /// card) plus the bank's redirect the window follows.
    /// </summary>
    public sealed class ContingencySnapshot
    {
        /// <summary>threeDomainSecure.status — empty when no challenge is asked for.</summary>
        public string? Status { get; init; }

        /// <summary>threeDomainSecure.redirectUrl.href — the bank's challenge page.</summary>
        public string? RedirectUrl { get; init; }

        /// <summary>threeDomainSecure.method.</summary>
        public string? Method { get; init; }

        /// <summary>threeDomainSecure.parameter.</summary>
        public string? Parameter { get; init; }

        /// <summary>threeDSContingencyData … contingencyContext.jwtSpecification.jwtIssuer.</summary>
        public string? JwtIssuer { get; init; }

        /// <summary>… jwtSpecification.jwtOrgUnitId.</summary>
        public string? JwtOrgUnitId { get; init; }

        /// <summary>The referenceId both sources agree on (response JSON / challenge-page hidden input).</summary>
        public string? ReferenceId { get; init; }

        /// <summary>threeDSContingencyData … resolution.paymentCard.id — the resolver's creditCardId.</summary>
        public string? CreditCardId { get; init; }

        /// <summary>True when the response asks for a challenge at all.</summary>
        public bool RequiresChallenge =>
            !string.IsNullOrEmpty(Status) && !string.IsNullOrEmpty(RedirectUrl);
    }

    /// <summary>What a machine step reports back.</summary>
    public sealed class StageOutcome
    {
        public bool Ok { get; init; }
        public bool Retryable { get; init; }
        public int Status { get; init; }
        public string? Body { get; init; }
        public string? Error { get; init; }

        /// <summary>The machine reached the challenge window — the host drives it from here.</summary>
        public bool AwaitingChallenge { get; init; }

        /// <summary>The snapshot parsed from the submit response, when one was read.</summary>
        public ContingencySnapshot? Contingency { get; init; }

        public static StageOutcome Success(int status, string? body) =>
            new() { Ok = true, Status = status, Body = body };

        public static StageOutcome Retry(int status) =>
            new() { Retryable = true, Status = status, Error = "paypal 3ds: HTTP " + status };

        public static StageOutcome Failed(int status) =>
            new() { Status = status, Error = "paypal 3ds: HTTP " + status };

        /// <summary>The machine stopped at the window — a real state, not an error.</summary>
        public static StageOutcome Challenge(ContingencySnapshot snapshot) =>
            new() { AwaitingChallenge = true, Contingency = snapshot,
                    Error = "paypal 3ds: challenge window required (" + snapshot.RedirectUrl + ")" };
    }

    /// <summary>The stage text selector both builders apply to the ctx+144 flag.</summary>
    public static string StatusText(bool challengeActive) =>
        challengeActive ? ProcessingStatus : SolvingStatus;

    /// <summary>
    /// The normal dialect's header wall, in the builder's own order (sub_141102970).
    /// </summary>
    public static IReadOnlyDictionary<string, string> NormalHeaders(StageInput i) => new Dictionary<string, string>
    {
        ["sec-ch-ua"] = i.SecChUa ?? string.Empty,
        ["x-paypal-internal-euat"] = i.Euat ?? string.Empty,
        ["paypal-client-metadata-id"] = i.MetadataId ?? string.Empty,
        ["sec-ch-ua-mobile"] = "?0",
        ["user-agent"] = i.UserAgent ?? string.Empty,
        ["content-type"] = "application/json",
        ["accept"] = "*/*",
        ["x-app-name"] = AppName,
        ["sec-ch-ua-platform"] = i.SecChUaPlatform ?? string.Empty,
        ["origin"] = "https://www.paypal.com",
        ["sec-fetch-site"] = "same-origin",
        ["sec-fetch-mode"] = "cors",
        ["sec-fetch-dest"] = "empty",
        ["referer"] = "https://www.paypal.com",
        ["Accept-Encoding"] = "gzip, deflate",
        ["Accept-Language"] = "en-GB",
    };

    /// <summary>The hosted dialect's header wall (sub_141105A80).</summary>
    public static IReadOnlyDictionary<string, string> HostedHeaders(StageInput i) => new Dictionary<string, string>
    {
        ["sec-ch-ua-platform"] = i.SecChUaPlatform ?? string.Empty,
        ["sec-ch-ua"] = i.SecChUa ?? string.Empty,
        ["sec-ch-ua-mobile"] = "?0",
        ["x-requested-with"] = "fetch",
        ["accept"] = "*/*",
        ["content-type"] = "application/json",
        ["x-locale"] = "en_US",
        ["paypal-client-context"] = i.MetadataId ?? string.Empty,
        ["x-app-name"] = i.HostedAppName ?? string.Empty,
        ["x-paypal-internal-euat"] = i.Euat ?? string.Empty,
        ["paypal-client-metadata-id"] = i.MetadataId ?? string.Empty,
        ["user-agent"] = i.UserAgent ?? string.Empty,
        ["x-country"] = i.Country ?? string.Empty,
        ["referer"] = i.HostedReferer ?? string.Empty,
        ["accept-encoding"] = "gzip, deflate, br, zstd",
        ["accept-language"] = "en-US,en;q=0.9",
        ["priority"] = "u=1, i",
    };

    /// <summary>
    /// One graphql stage request. R1095 corrects the shape: PayPal puts the operation name in
    /// the <b>URL query string</b> (<c>https://www.paypal.com/graphql?GetThreeDsJwtQuery</c>,
    /// 0x147097f60) and sends the <b>full document</b> in the body's <c>query</c> field beside
    /// <c>variables</c> — the four documents are the frozen literals above. R1086 had inferred
    /// Stripe's persisted-operation envelope (<c>{"operationName": N, ...}</c>) here; that was
    /// the wrong integration's shape and this helper now follows PayPal's own.
    /// The wall, the budget and the dispatch are the builders' own.
    /// </summary>
    public static async Task<StageOutcome> GqlAsync(FlowContext c, StageInput input, string operationName,
        JObject variables, CancellationToken ct, string? url = null, string? document = null)
    {
        c.Emit(StatusText(input.ChallengeActive), "StatusInfo");

        var options = c.Options("paypal-3ds");
        options.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
        foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
            options.Headers[h.Key] = h.Value;

        var body = new JObject
        {
            ["variables"] = variables,
            ["query"] = document ?? DocumentFor(operationName),
        };
        options.Content = new StringContent(body.ToString(Newtonsoft.Json.Formatting.None),
            System.Text.Encoding.UTF8, "application/json");

        // The frozen literal is the target; the session var is the replica's standard test/config
        // seam (StoreFlow's checkStockUrl convention), so the gateway can drive the resolver
        // against a configured endpoint without the frozen URL being mutable in the protocol.
        // The operation name rides the query string, which is the image's own composition.
        var baseUrl = url
                      ?? (c.Session.Vars.TryGetValue("paypal3ds.graphqlUrl", out var gqlOverride) &&
                          !string.IsNullOrEmpty(gqlOverride)
                          ? gqlOverride
                          : GraphqlUrl);
        var target = baseUrl.TrimEnd('/') + "?" + operationName;

        var res = await c.Http.SendAsync(HttpMethod.Put, target, options, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(res.Cookies);

        // The dispatch the builders register: 200 reaches the success continuation, and
        // 403 and 429 share one retry closure. Everything else is unhandled — a fail, not a retry.
        if (res.StatusCode == 200) return StageOutcome.Success(200, res.Body);
        if (res.StatusCode is 403 or 429) return StageOutcome.Retry(res.StatusCode);
        return StageOutcome.Failed(res.StatusCode);
    }

    /// <summary>
    /// Reads the contingency out of a submit response — the needles the case bodies pull
    /// (jwtSpecification / referenceId / the card's id), plus the bank's redirect the window follows.
    /// </summary>
    public static ContingencySnapshot ReadContingency(string? body)
    {
        JObject root;
        try { root = JObject.Parse(body ?? "{}"); }
        catch { return new ContingencySnapshot(); }

        string? Dig(params string[] path)
        {
            JToken? t = root;
            foreach (var p in path) t = t?[p];
            return t?.Type == JTokenType.Null ? null : t?.ToString();
        }

        return new ContingencySnapshot
        {
            Status = Dig("data", "paymentContingencies", "threeDomainSecure", "status")
                     ?? Dig("paymentContingencies", "threeDomainSecure", "status"),
            RedirectUrl = Dig("data", "paymentContingencies", "threeDomainSecure", "redirectUrl", "href")
                          ?? Dig("paymentContingencies", "threeDomainSecure", "redirectUrl", "href"),
            Method = Dig("data", "paymentContingencies", "threeDomainSecure", "method")
                     ?? Dig("paymentContingencies", "threeDomainSecure", "method"),
            Parameter = Dig("data", "paymentContingencies", "threeDomainSecure", "parameter")
                        ?? Dig("paymentContingencies", "threeDomainSecure", "parameter"),
            JwtIssuer = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                            "contingencyContext", "jwtSpecification", "jwtIssuer")
                        ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                               "contingencyContext", "jwtSpecification", "jwtIssuer"),
            JwtOrgUnitId = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                               "contingencyContext", "jwtSpecification", "jwtOrgUnitId")
                           ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                                  "contingencyContext", "jwtSpecification", "jwtOrgUnitId"),
            ReferenceId = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                              "contingencyContext", "referenceId")
                          ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                                 "contingencyContext", "referenceId"),
            CreditCardId = Dig("data", "paymentContingencies", "threeDSContingencyData", "resolution",
                               "paymentCard", "id")
                           ?? Dig("paymentContingencies", "threeDSContingencyData", "resolution",
                                  "paymentCard", "id"),
        };
    }

    /// <summary>
    /// Submit3DS → the machine's synchronous reach: the submit stage reads the contingency, and a
    /// response that asks for a challenge fetches the JWT for the window before handing the
    /// window over to the host — the original's own stopping point (the window is driven by the
    /// offscreen browser pool, not by this state machine).
    /// </summary>
    public async Task<StageOutcome> RunAsync(FlowContext c, StageInput input, CancellationToken ct,
        string? url = null)
    {
        var submit = await SubmitAsync(c, input, ct, url).ConfigureAwait(false);
        if (!submit.Ok) return submit;
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Process3DS);

        var snapshot = ReadContingency(submit.Body);
        if (!snapshot.RequiresChallenge)
        {
            // No challenge asked for: the payment state is the response's, and the machine is done.
            c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Complete3DS);
            return StageOutcome.Success(submit.Status, submit.Body);
        }

        // Process3DS: the JWT the window's post-back carries. The case bodies' variables read
        // the amount formatted {0:0.00} beside the contingency fields.
        var jwtVariables = new JObject
        {
            ["amount"] = input.Amount.ToString("0.00"),
            ["jwtIssuer"] = snapshot.JwtIssuer,
            ["jwtOrgUnitId"] = snapshot.JwtOrgUnitId,
            ["referenceId"] = snapshot.ReferenceId,
        };
        var jwt = await GqlAsync(c, input, JwtQueryOperation, jwtVariables, ct, url).ConfigureAwait(false);
        if (!jwt.Ok) return jwt;
        c.Session.Vars["paypal3ds.jwt"] = jwt.Body ?? string.Empty;

        // R1096: the device-data pair the JWT query exists to feed, decoded from the case bodies
        // (PUT site at line 962 of the hosted solver): the JWT form goes to the response's own
        // deviceDataCollectionUrl.href when it names one, else to the frozen init-method endpoint
        // (0x1470985e8); then notify-method-cmpl (0x147098740) takes the base64
        // {"threeDSServerTransID": …} envelope in its threeDSMethodData field (0x14716d3d0).
        var deviceStep = await SubmitDeviceDataAsync(c, input, jwt.Body, ct).ConfigureAwait(false);
        if (!deviceStep.Ok) return deviceStep;

        // Waiting3DS: the window itself. Its page, size and post-back fields are the decoded
        // constants — the host drives the browser; what it posts back is JWT and MD. The machine
        // state and the resolver's inputs persist on the session so the gateway's action
        // completion (CompleteActionAsync) can rebuild the snapshot and drive ContinueAsync.
        c.Session.Vars["paypal3ds.redirectUrl"] = snapshot.RedirectUrl ?? string.Empty;
        c.Session.Vars["paypal3ds.referenceId"] = snapshot.ReferenceId ?? string.Empty;
        c.Session.Vars["paypal3ds.creditCardId"] = snapshot.CreditCardId ?? string.Empty;
        c.Session.Vars["paypal3ds.euat"] = input.Euat ?? string.Empty;
        c.Session.Vars["paypal3ds.hosted"] = input.Hosted ? "1" : "0";
        c.Session.Vars["paypal3ds.token"] = input.Token ?? string.Empty;
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Waiting3DS);
        return StageOutcome.Challenge(snapshot);
    }

    /// <summary>
    /// The 3DS2 device-data pair (R1096). The JWT the query returned is POSTed as the
    /// <c>JWT</c> form field to the device-data collection URL — the response's own
    /// <c>deviceDataCollectionUrl.href</c> (needle 0x147003a88 → 0x1470494a8) when present, else
    /// the frozen <c>init-method</c> endpoint (0x1470985e8). The completion then notifies
    /// <c>notify-method-cmpl</c> (0x147098740) with <c>threeDSMethodData</c> (0x14716d3d0), whose
    /// value is the base64 of <c>{"threeDSServerTransID": …}</c> (0x14716d5f8).
    ///
    /// <para>
    /// The hosted solver gates this pair on its <c>alive</c> flag (sub_140f9e790 — the same flag
    /// R1091's stop line prints), so a machine without a live challenge context skips it. That is
    /// the gate reproduced here: without a JWT there is nothing to collect.
    /// </para>
    /// </summary>
    public async Task<StageOutcome> SubmitDeviceDataAsync(FlowContext c, StageInput input,
        string? jwtBody, CancellationToken ct)
    {
        var jwt = ReadNeedle(jwtBody, "jwt");
        if (string.IsNullOrEmpty(jwt)) return StageOutcome.Success(200, null);   // not alive: skip

        // The collection target: the answer's own href, else the frozen init-method endpoint.
        var collection = ReadNestedNeedle(jwtBody,
            DeviceDataCollectionUrlField, "href") ?? InitMethodUrl;
        if (c.Session.Vars.TryGetValue("paypal3ds.initMethodUrl", out var initOverride) &&
            !string.IsNullOrEmpty(initOverride))
            collection = initOverride;

        var jwtForm = new System.Net.Http.FormUrlEncodedContent(new Dictionary<string, string>
        {
            [JwtFormField] = jwt,                                  // 0x146dd3a08
        });
        var jwtOptions = c.Options("paypal3ds-init-method");
        jwtOptions.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
        jwtOptions.Content = jwtForm;
        foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
            jwtOptions.Headers[h.Key] = h.Value;

        var init = await c.Http.SendAsync(HttpMethod.Post, collection, jwtOptions, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(init.Cookies);
        if (init.StatusCode is < 200 or >= 300)
            return StageOutcome.Failed(init.StatusCode);

        // The notification: threeDSMethodData = base64({"threeDSServerTransID": <id>}).
        var txnId = ReadNeedle(jwtBody, ThreeDsServerTransIdField)
                    ?? c.Session.Vars.GetValueOrDefault("paypal3ds.threeDsServerTransId")
                    ?? string.Empty;
        var envelope = new JObject { [ThreeDsServerTransIdField] = txnId };
        var methodData = Convert.ToBase64String(
            System.Text.Encoding.UTF8.GetBytes(envelope.ToString(Newtonsoft.Json.Formatting.None)));

        var notifyBase = c.Session.Vars.TryGetValue("paypal3ds.notifyUrl", out var notifyOverride) &&
                         !string.IsNullOrEmpty(notifyOverride)
            ? notifyOverride
            : NotifyMethodCompleteUrl;

        var notifyOptions = c.Options("paypal3ds-notify-method");
        notifyOptions.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
        notifyOptions.Content = new System.Net.Http.FormUrlEncodedContent(new Dictionary<string, string>
        {
            [ThreeDsMethodDataField] = methodData,                  // 0x14716d3d0
        });
        foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
            notifyOptions.Headers[h.Key] = h.Value;

        var notify = await c.Http.SendAsync(HttpMethod.Put, notifyBase, notifyOptions, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(notify.Cookies);
        if (notify.StatusCode is < 200 or >= 300) return StageOutcome.Failed(notify.StatusCode);

        c.Session.Vars["paypal3ds.threeDSMethodData"] = methodData;
        return StageOutcome.Success(notify.StatusCode, notify.Body);
    }

    /// <summary>
    /// The normal path's session bootstrap (R1097, corrected in R1098 against the assembly at
    /// <c>sub_140d8d2b0</c> lines 268–317): both hops are <b>JSON</b> PUTs, not forms —
    /// serverData carries <c>{"token": &lt;cartId&gt;}</c> (key 0x147171d48) and the session hop
    /// carries <c>{"token": &lt;cartId&gt;, "action": "verify"}</c> (keys 0x147171d48 +
    /// 0x146f6d9a8, the literal 0x14717e4a8). The entry URL the first hop is built from is the
    /// frozen <c>threeDS?action=verify&amp;flow=3ds&amp;cart_id=</c> prefix + the cart id +
    /// <c>&amp;go_to=next</c> (0x146a7f400). Either hop refused speaks the path's own failure
    /// line, <c>Payment failed (3DS)</c> (0x146e3b5f0) in <c>#FB4961</c> (0x146a76fd0).
    /// </summary>
    public async Task<StageOutcome> SubmitNormalBootstrapAsync(FlowContext c, StageInput input,
        string cartId, CancellationToken ct)
    {
        string Seam(string key, string frozen) =>
            c.Session.Vars.TryGetValue(key, out var v) && !string.IsNullOrEmpty(v) ? v : frozen;

        // The entry URL the machine composes before the first hop (line 264).
        c.Session.Vars["paypal3ds.helios.entryUrl"] = EntryUrlFor(cartId);

        var hops = new (string Target, string Json, string Tag)[]
        {
            (Seam("paypal3ds.heliosServerDataUrl", HeliosServerDataUrl),
                new JObject { [TokenField] = cartId }.ToString(Newtonsoft.Json.Formatting.None),
                "paypal3ds-helios-serverdata"),
            (Seam("paypal3ds.heliosSessionUrl", HeliosSessionUrl),
                new JObject { [TokenField] = cartId, [ActionField] = VerifyAction }
                    .ToString(Newtonsoft.Json.Formatting.None),
                "paypal3ds-helios-session"),
        };

        foreach (var (target, json, tag) in hops)
        {
            var options = c.Options(tag);
            options.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
            options.Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
                options.Headers[h.Key] = h.Value;

            var res = await c.Http.SendAsync(HttpMethod.Put, target, options, ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            if (res.StatusCode is < 200 or >= 300)
            {
                c.Emit(NormalPathFailureStatus, NormalPathFailureColour);
                return StageOutcome.Failed(res.StatusCode);
            }
            c.Session.Vars["paypal3ds.helios." + (tag.EndsWith("session") ? "session" : "serverData")]
                = res.Body ?? string.Empty;
        }

        return StageOutcome.Success(200, null);
    }

    /// <summary>The entry URL composition (frozen prefix + cart id + the go_to segment).</summary>
    public static string EntryUrlFor(string cartId) =>
        HeliosEntryUrl + Uri.EscapeDataString(cartId) + GoToNextSegment;

    /// <summary>
    /// Which PayPal 3DS surface to drive. R1100 established that the image does not branch on a
    /// field inside a shared function: the two solvers are two implementation types with parallel
    /// method tables (normal at 0x1475d4950, hosted at 0x14760b61c — each slot pair holding its
    /// own starter plus one more method), so the choice is made by which type is constructed.
    /// This enum is that choice made explicit at the API.
    /// </summary>
    public enum ThreeDsDialect { Hosted, Normal }

    /// <summary>
    /// Drives the dialect that was selected. <see cref="ThreeDsDialect.Hosted"/> walks the
    /// graphql + <c>payment-authentication</c> chain; <see cref="ThreeDsDialect.Normal"/> walks
    /// the <c>heliosnext</c> chain. The two share only the method pair, which is why they are two
    /// entry points rather than one function with a flag.
    /// </summary>
    public Task<StageOutcome> RunDialectAsync(FlowContext c, StageInput input,
        ThreeDsDialect dialect, CancellationToken ct, string? graphqlUrl = null,
        string? cartId = null) => dialect switch
    {
        ThreeDsDialect.Normal => RunNormalAsync(c, input, cartId ?? string.Empty, ct, graphqlUrl),
        _ => RunAsync(c, input, ct, graphqlUrl),
    };

    /// <summary>
    /// The normal dialect end to end (R1099) — the counterpart of <see cref="RunAsync"/> for the
    /// <c>heliosnext</c> surface, mirroring how the image has two solver entry points
    /// (<c>sub_140d8d2b0</c> for this one, <c>sub_141113680</c> for the hosted one). The order is
    /// the normal solver's own: session bootstrap (serverData → session) → the JWT query → the
    /// method pair (init-method → notify-method-cmpl) → the challenge initialisation → the
    /// confirmation hop. It stops where the challenge window opens, exactly as the hosted path
    /// does, because the window is host-driven in both dialects.
    /// </summary>
    public async Task<StageOutcome> RunNormalAsync(FlowContext c, StageInput input, string cartId,
        CancellationToken ct, string? graphqlUrl = null)
    {
        var boot = await SubmitNormalBootstrapAsync(c, input, cartId, ct).ConfigureAwait(false);
        if (!boot.Ok) return boot;
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Process3DS);

        // The submit stage is the same graphql contingency read the hosted path performs.
        var submit = await SubmitAsync(c, input, ct, graphqlUrl).ConfigureAwait(false);
        if (!submit.Ok) return submit;

        var snapshot = ReadContingency(submit.Body);
        if (!snapshot.RequiresChallenge)
        {
            c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Complete3DS);
            return StageOutcome.Success(submit.Status, submit.Body);
        }

        var jwtVariables = new JObject
        {
            ["amount"] = input.Amount.ToString("0.00"),
            ["jwtIssuer"] = snapshot.JwtIssuer,
            ["jwtOrgUnitId"] = snapshot.JwtOrgUnitId,
            ["referenceId"] = snapshot.ReferenceId,
        };
        var jwt = await GqlAsync(c, input, JwtQueryOperation, jwtVariables, ct, graphqlUrl)
            .ConfigureAwait(false);
        if (!jwt.Ok) return jwt;
        c.Session.Vars["paypal3ds.jwt"] = jwt.Body ?? string.Empty;

        // The method pair, then the challenge initialisation — this dialect's own two hops.
        var method = await SubmitDeviceDataAsync(c, input, jwt.Body, ct).ConfigureAwait(false);
        if (!method.Ok) return method;

        var challenge = await SubmitChallengeInitAsync(c, input, jwt.Body, ct).ConfigureAwait(false);
        if (!challenge.Ok) return challenge;

        // Waiting3DS: the window opens here in both dialects; the resolver inputs persist.
        c.Session.Vars["paypal3ds.redirectUrl"] = snapshot.RedirectUrl ?? string.Empty;
        c.Session.Vars["paypal3ds.referenceId"] = snapshot.ReferenceId ?? string.Empty;
        c.Session.Vars["paypal3ds.creditCardId"] = snapshot.CreditCardId ?? string.Empty;
        c.Session.Vars["paypal3ds.euat"] = input.Euat ?? string.Empty;
        c.Session.Vars["paypal3ds.hosted"] = "0";
        c.Session.Vars["paypal3ds.token"] = input.Token ?? string.Empty;
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Waiting3DS);
        return StageOutcome.Challenge(snapshot);
    }

    /// <summary>
    /// The normal path's confirmation hop (line 591): a PUT to the context's URL at +8 when it
    /// carries one, else the frozen <c>processThreedsConfirmation</c> endpoint (0x147098258), with
    /// the content the context pre-built.
    /// </summary>
    public async Task<StageOutcome> SubmitProcessConfirmationAsync(FlowContext c, StageInput input,
        string? json, CancellationToken ct)
    {
        var target = c.Session.Vars.GetValueOrDefault("paypal3ds.processConfirmationUrl");
        if (string.IsNullOrEmpty(target)) target = HeliosProcessThreedsConfirmationUrl;

        var options = c.Options("paypal3ds-helios-process");
        options.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
        options.Content = new StringContent(json ?? "{}", System.Text.Encoding.UTF8, "application/json");
        foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
            options.Headers[h.Key] = h.Value;

        var res = await c.Http.SendAsync(HttpMethod.Put, target, options, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(res.Cookies);
        if (res.StatusCode is < 200 or >= 300)
        {
            c.Emit(NormalPathFailureStatus, NormalPathFailureColour);
            return StageOutcome.Failed(res.StatusCode);
        }

        c.Session.Vars["paypal3ds.processConfirmation"] = res.Body ?? string.Empty;
        return StageOutcome.Success(res.StatusCode, res.Body);
    }

    /// <summary>
    /// The challenge initialisation hop (R1097, normal path only): the JWT form (0x146dd3a08) to
    /// the URL the context names at +96 when it has one, else the frozen
    /// <c>init-challenge</c> endpoint (0x147098540) — the same "context value else frozen default"
    /// shape the method hop uses.
    /// </summary>
    public async Task<StageOutcome> SubmitChallengeInitAsync(FlowContext c, StageInput input,
        string? jwtBody, CancellationToken ct)
    {
        var jwt = ReadNeedle(jwtBody, "jwt");
        if (string.IsNullOrEmpty(jwt)) return StageOutcome.Success(200, null);   // nothing to initialise

        var target = c.Session.Vars.GetValueOrDefault("paypal3ds.initChallengeUrl");
        if (string.IsNullOrEmpty(target)) target = InitChallengeUrl;

        var options = c.Options("paypal3ds-init-challenge");
        options.Timeout = TimeSpan.FromMilliseconds(StageTimeoutMs);
        // R1102 correction: the form carries ONLY the JWT (0x146dd3a08, value ctx+0x58). The
        // challenge_callback_url string is not a field of this request at all — the machine READS
        // it out of the answer's own "payload" object (0x14710e630 → 0x146fc54d8 at 0x140d8e6ff)
        // and stashes it at ctx+0x30. R1101 had put it in the form; that is undone here.
        options.Content = new System.Net.Http.FormUrlEncodedContent(new Dictionary<string, string>
        {
            [JwtFormField] = jwt,
        });
        foreach (var h in (input.Hosted ? HostedHeaders(input) : NormalHeaders(input)))
            options.Headers[h.Key] = h.Value;

        var res = await c.Http.SendAsync(HttpMethod.Put, target, options, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(res.Cookies);
        if (res.StatusCode is < 200 or >= 300)
        {
            c.Emit(NormalPathFailureStatus, NormalPathFailureColour);
            return StageOutcome.Failed(res.StatusCode);
        }

        // R1102: the answer's payload carries the callback URL the machine stashes at ctx+0x30
        // (read "payload" then "challenge_callback_url", disassembly at 0x140d8e6e7/0x140d8e6ff).
        var callback = ReadNestedNeedle(res.Body, PayloadField, ChallengeCallbackUrlField)
                       ?? ReadNeedle(res.Body, ChallengeCallbackUrlField);
        if (!string.IsNullOrEmpty(callback))
            c.Session.Vars["paypal3ds.challengeCallbackUrl"] = callback;

        c.Session.Vars["paypal3ds.challengeInit"] = res.Body ?? string.Empty;
        return StageOutcome.Success(res.StatusCode, res.Body);
    }

    /// <summary>Read one top-level string out of a response body, null when absent.</summary>
    private static string? ReadNeedle(string? body, string key)
    {
        if (string.IsNullOrEmpty(body)) return null;
        try { return JObject.Parse(body)[key]?.ToString(); }
        catch { return null; }
    }

    /// <summary>Read <c>outer.inner</c> out of a response body, null when absent.</summary>
    private static string? ReadNestedNeedle(string? body, string outer, string inner)
    {
        if (string.IsNullOrEmpty(body)) return null;
        try { return JObject.Parse(body)[outer]?[inner]?.ToString(); }
        catch { return null; }
    }

    /// <summary>
    /// Completes the machine after the challenge window answered — ThreeDsAuthenticateMutation,
    /// ThreeDsLookUpMutation, then ResolveThreeDsContingency with the six variables
    /// (token / authId / referenceId / creditCardId / status / experiences).
    /// </summary>
    public async Task<StageOutcome> ContinueAsync(FlowContext c, StageInput input, ContingencySnapshot snapshot,
        string authId, string status, CancellationToken ct, string? url = null)
    {
        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Process3DS);

        var authVariables = new JObject
        {
            ["authId"] = authId,
            ["referenceId"] = snapshot.ReferenceId,
            ["creditCardId"] = snapshot.CreditCardId,
        };
        var auth = await GqlAsync(c, input, AuthenticateOperation, authVariables, ct, url).ConfigureAwait(false);
        if (!auth.Ok) return auth;

        var lookVariables = new JObject
        {
            ["referenceId"] = snapshot.ReferenceId,
            ["creditCardId"] = snapshot.CreditCardId,
        };
        var look = await GqlAsync(c, input, LookUpOperation, lookVariables, ct, url).ConfigureAwait(false);
        if (!look.Ok) return look;

        var resolveVariables = new JObject
        {
            ["token"] = input.Token,
            ["authId"] = authId,
            ["referenceId"] = snapshot.ReferenceId,
            ["creditCardId"] = snapshot.CreditCardId,
            ["status"] = status,
            ["experiences"] = new JArray("HERMES", "EXPRESS_CHECKOUT"),   // the decoded dialect set
        };
        var resolve = await GqlAsync(c, input, ResolveOperation, resolveVariables, ct, url).ConfigureAwait(false);
        if (!resolve.Ok) return resolve;

        c.Session.Vars["paypal3ds.state"] = nameof(ThreeDsState.Complete3DS);
        return StageOutcome.Success(resolve.Status, resolve.Body);
    }

    /// <summary>
    /// Stage 1, both dialects: the white StatusInfo wall, the thirty-second budget, the exact
    /// header dialect, and the PUT to PayPal's graphql surface with the caller's operation.
    /// The original's submit carried the first persisted operation; the helper above is the
    /// general form, and this step keeps its named place in the four-state machine.
    /// </summary>
    public static async Task<StageOutcome> SubmitAsync(FlowContext c, StageInput input, CancellationToken ct,
        string? url = null)
    {
        var submitVariables = new JObject
        {
            ["token"] = input.Token,
            ["amount"] = input.Amount.ToString("0.00"),
        };
        return await GqlAsync(c, input, JwtQueryOperation, submitVariables, ct, url).ConfigureAwait(false);
    }
}
