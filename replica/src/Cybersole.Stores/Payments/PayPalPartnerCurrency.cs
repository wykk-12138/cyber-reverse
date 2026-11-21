using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The PayPal partner currency conversion — <c>CurrencyConversion</c> — read out of the image.
///
/// <para>
/// <b>Observed</b>, from the sender at <c>sub_14110F8C0</c> (1173 bytes) and the document at 0x1470D0FB4:
/// the base <c>https://www.paypal.com/graphql/</c> (the same one the approval uses), the operation name, the
/// envelope keys, the content type, and the three variable keys the sender writes — <c>token</c>,
/// <c>conversionType</c> and <c>expeirences</c>. That last spelling is the image's: the document declares
/// <c>$experiences</c> and the sender sends <c>expeirences</c>. A faithful replica sends it the same way.
/// </para>
///
/// <para>
/// <b>Observed</b> enum: <c>VENDOR</c> (0x146F1AF90), which belongs to <c>conversionType</c>; the enum's other
/// members are not in this function, so callers may pass their own.
/// </para>
/// </summary>
public static class PayPalPartnerCurrency
{
    /// <summary>The shared partner base URL, from 0x147097E78. Same string the approval uses.</summary>
    public const string BaseUrl = PayPalPartnerApprove.BaseUrl;

    /// <summary>The operation name the image sends, from 0x146BAAEC8.</summary>
    public const string OperationName = "CurrencyConversion";

    /// <summary>The endpoint: base plus operation name.</summary>
    public const string Url = BaseUrl + OperationName;

    /// <summary>The document, 10406 characters from 0x1470D0FB4.</summary>
    public const string Document = @"mutation CurrencyConversion($conversionType: CheckoutCurrencyConversionType!, $experiences: [ThreeDSPaymentExperience], $token: String!) {
  updateCurrencyConversionType(token: $token, conversionType: $conversionType) {
    fundingOptions(returnAllPlans: true, groupSourcesOnType: INCENTIVE) {
      ...FundingOptionFragment
      __typename
    }
    paymentContingencies {
      ...PaymentContingenciesFragment
      threeDomainSecure(experiences: $experiences) {
        ...ThreeDomainSecureFields
        __typename
      }
      __typename
    }
    cart {
      amounts {
        total {
          currencyValue
          currencyFormat
          currencyCode
          currencyFormatSymbolISOCurrency
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
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
";

    /// <summary>
    /// The three variable keys the sender writes, in its own spelling — including <c>expeirences</c>, which the
    /// document calls <c>$experiences</c>. Asserting that pairing is what stops a future edit from "fixing" it.
    /// </summary>
    public static readonly string[] VariableNames = { "token", "conversionType", "expeirences" };

    /// <summary>The conversion type the sender names, from 0x146F1AF90.</summary>
    public const string ConversionTypeVendor = "VENDOR";

    /// <summary>The request body: the envelope the sender builds.</summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Ask for the conversion. Returns the <c>updateCurrencyConversionType</c> node, whose first useful child is
    /// <c>fundingOptions</c> with the converted amounts, or null with the reason in <paramref name="error"/>.
    /// </summary>
    public static async Task<(JObject? Conversion, string Error)> ConvertAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        if (variables?["token"] is null || string.IsNullOrEmpty(variables["token"]!.ToString()))
            return (null, "currency: no token — the conversion is keyed by the buyer token");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? Url, Envelope(variables), "paypal-currency", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "currency: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "currency: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var conversion = reply["data"]?["updateCurrencyConversionType"] as JObject;
            return conversion is null ? (null, "currency: no conversion in reply") : (conversion, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "currency: " + ex.GetType().Name);
        }
    }
}
