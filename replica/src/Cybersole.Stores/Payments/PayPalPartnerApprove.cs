using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The PayPal partner approval — <c>approveMemberPayment</c> — read out of the image.
///
/// <para>
/// <b>Observed</b>, all from the sender at <c>sub_14110C600</c> (1647 bytes) and the document at 0x1470E9FA4:
/// the base URL <c>https://www.paypal.com/graphql/</c> (0x147097E78, 31 characters, with the trailing slash),
/// the operation name, the envelope keys (<c>operationName</c>, <c>query</c>, <c>variables</c>) and the
/// content type <c>application/json</c>; the eleven variable names; and the two enum literals
/// <c>IFRAME</c> and <c>INSTANT</c>.
/// </para>
///
/// <para>
/// <b>Inference:</b> that <c>IFRAME</c> and <c>INSTANT</c> belong to <c>fundingMethodType</c>. The image puts
/// both in this function beside that variable's name, but no assignment pairs them, so they are exposed as
/// constants and a caller chooses rather than this class guessing.
/// </para>
/// </summary>
public static class PayPalPartnerApprove
{
    /// <summary>The observed base URL, trailing slash included, from 0x147097E78.</summary>
    public const string BaseUrl = "https://www.paypal.com/graphql/";

    /// <summary>The operation name the image sends, from 0x146F79800.</summary>
    public const string OperationName = "approveMemberPayment";

    /// <summary>The endpoint the image composes: base plus operation name.</summary>
    public const string Url = BaseUrl + OperationName;

    /// <summary>The document, 5407 characters from 0x1470E9FA4.</summary>
    public const string Document = @"mutation approveMemberPayment($token: String!, $selectedAddressId: String, $preferredShippingAddressId: String, $selectedFundingOptionId: String!, $preferredFundingOptionId: String, $secondaryFundingOptionIds: [String!], $selectedInstallmentOption: InstallmentsInput, $rewards: RewardsInput, $preAuthorizationRequired: Boolean, $fundingMethodType: FundingInstrumentMethodType, $shareAddressWithDonatee: Boolean, $setStickyFiRequired: Boolean, $scaCompleted: Boolean!, $experiences: [ThreeDSPaymentExperience], $cryptocurrencyQuoteId: String) {
  approveMemberPayment(token: $token, selectedAddressId: $selectedAddressId, preferredShippingAddressId: $preferredShippingAddressId, primaryFundingOptionId: $selectedFundingOptionId, preferredFundingOptionId: $preferredFundingOptionId, secondaryFundingOptionIds: $secondaryFundingOptionIds, selectedInstallmentOption: $selectedInstallmentOption, rewards: $rewards, preAuthorizationRequired: $preAuthorizationRequired, fundingMethodType: $fundingMethodType, shareAddressWithDonatee: $shareAddressWithDonatee, setStickyFiRequired: $setStickyFiRequired, strongCustomerAuthenticationCompleted: $scaCompleted, cryptocurrencyQuoteId: $cryptocurrencyQuoteId) {
    state
    buyer {
      userId
      email {
        stringValue
        __typename
      }
      name {
        fullName
        __typename
      }
      __typename
    }
    cart {
      intent
      paymentId
      billingToken
      returnUrl {
        href
        pathname
        __typename
      }
      cancelUrl {
        href
        pathname
        __typename
      }
      intent
      items {
        quantity
        name
        sku
        unitPrice {
          currencyValue
          __typename
        }
        itemOptionSelections {
          name
          description
          __typename
        }
        __typename
      }
      amounts {
        subtotal {
          currencyCode
          currencyFormat
          __typename
        }
        tax {
          currencyCode
          currencyFormat
          __typename
        }
        shipping {
          currencyCode
          currencyFormat
          __typename
        }
        insurance {
          currencyCode
          currencyFormat
          __typename
        }
        handlingFee {
          currencyCode
          currencyFormat
          __typename
        }
        total {
          currencyCode
          currencyFormat
          __typename
        }
        discount {
          currencyCode
          currencyFormat
          __typename
        }
        __typename
      }
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
    completedPaymentInfo {
      transactionId
      transactionState
      softDescriptor
      postbackData
      __typename
    }
    merchant {
      preferences {
        autoReturnToMerchant
        enablePaymentDataTransfer
        returnUrl
        __typename
      }
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
";

    /// <summary>The eleven variable names the sender fills, in the image's own spelling.</summary>
    /// <summary>
    /// The same mutation with one more declared variable: <c>paycodeEncrypted</c>. 5620 characters from 0x1470EC9FC,
    /// against the 5407-character document above. The declared sets are identical apart from that name, which is the
    /// whole of the difference — so the dialect follows the funding option, not the store.
    /// </summary>
    public const string PaycodeDocument = @"mutation approveMemberPayment($token: String!, $selectedAddressId: String, $preferredShippingAddressId: String, $selectedFundingOptionId: String!, $preferredFundingOptionId: String, $secondaryFundingOptionIds: [String!], $selectedInstallmentOption: InstallmentsInput, $rewards: RewardsInput, $preAuthorizationRequired: Boolean, $fundingMethodType: FundingInstrumentMethodType, $shareAddressWithDonatee: Boolean, $setStickyFiRequired: Boolean, $scaCompleted: Boolean!, $experiences: [ThreeDSPaymentExperience], $cryptocurrencyQuoteId: String, $paycodeEncrypted: String) {
  approveMemberPayment(
    token: $token
    selectedAddressId: $selectedAddressId
    preferredShippingAddressId: $preferredShippingAddressId
    primaryFundingOptionId: $selectedFundingOptionId
    preferredFundingOptionId: $preferredFundingOptionId
    secondaryFundingOptionIds: $secondaryFundingOptionIds
    selectedInstallmentOption: $selectedInstallmentOption
    rewards: $rewards
    preAuthorizationRequired: $preAuthorizationRequired
    fundingMethodType: $fundingMethodType
    shareAddressWithDonatee: $shareAddressWithDonatee
    setStickyFiRequired: $setStickyFiRequired
    strongCustomerAuthenticationCompleted: $scaCompleted
    cryptocurrencyQuoteId: $cryptocurrencyQuoteId
    paycodeEncrypted: $paycodeEncrypted
  ) {
    state
    buyer {
      userId
      email {
        stringValue
        __typename
      }
      name {
        fullName
        __typename
      }
      __typename
    }
    cart {
      intent
      paymentId
      billingToken
      returnUrl {
        href
        pathname
        __typename
      }
      cancelUrl {
        href
        pathname
        __typename
      }
      intent
      items {
        quantity
        name
        sku
        unitPrice {
          currencyValue
          __typename
        }
        itemOptionSelections {
          name
          description
          __typename
        }
        __typename
      }
      amounts {
        subtotal {
          currencyCode
          currencyFormat
          __typename
        }
        tax {
          currencyCode
          currencyFormat
          __typename
        }
        shipping {
          currencyCode
          currencyFormat
          __typename
        }
        insurance {
          currencyCode
          currencyFormat
          __typename
        }
        handlingFee {
          currencyCode
          currencyFormat
          __typename
        }
        total {
          currencyCode
          currencyFormat
          __typename
        }
        discount {
          currencyCode
          currencyFormat
          __typename
        }
        __typename
      }
      __typename
    }
    paymentContingencies {
      ...PaymentContingenciesFragment
      threeDomainSecure(experiences: $experiences) {
        ...ThreeDomainSecureFields
        __typename
      }
      paycodeRequired {
        causeName
        attempts
        name
        __typename
      }
      __typename
    }
    completedPaymentInfo {
      transactionId
      transactionState
      softDescriptor
      postbackData
      __typename
    }
    merchant {
      preferences {
        autoReturnToMerchant
        enablePaymentDataTransfer
        returnUrl
        __typename
      }
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
";

    /// <summary>The variable that decides between the two dialects.</summary>
    public const string PaycodeVariableName = "paycodeEncrypted";

    /// <summary>
    /// The document a payment needs. A funding option carrying an encrypted paycode declares it, and only then is the
    /// longer document the right one; everything else takes the document this class has always sent.
    /// </summary>
    public static string DocumentFor(bool carriesPaycode) => carriesPaycode ? PaycodeDocument : Document;

    /// <summary>The envelope for whichever dialect the payment needs.</summary>
    public static JObject EnvelopeFor(JObject variables)
    {
        var carriesPaycode = variables?[PaycodeVariableName] is not null;
        return new JObject
        {
            ["operationName"] = OperationName,
            ["query"] = DocumentFor(carriesPaycode),
            ["variables"] = variables ?? new JObject(),
        };
    }

    public static readonly string[] VariableNames =
    {
        "token", "selectedAddressId", "preferredShippingAddressId", "selectedFundingOptionId",
        "preferredFundingOptionId", "secondaryFundingOptionIds", "preAuthorizationRequired",
        "fundingMethodType", "setStickyFiRequired", "scaCompleted", "experiences",
    };

    /// <summary>The two enum literals that sit beside <c>fundingMethodType</c> in the sender.</summary>
    public const string FundingMethodIframe = "IFRAME";
    public const string FundingMethodInstant = "INSTANT";

    /// <summary>
    /// The request body: the operation name, the document and the variables, which is the envelope the sender
    /// builds. <paramref name="variables"/> is passed through rather than assembled here, because seven of the
    /// eleven are the caller's — a payment method id, an address id, a token — and inventing defaults for them
    /// would send a request the partner could accept with the wrong meaning.
    /// </summary>
    public static JObject Envelope(JObject variables) => new()
    {
        ["operationName"] = OperationName,
        ["query"] = Document,
        ["variables"] = variables,
    };

    /// <summary>
    /// Approve a member payment. Returns the GraphQL <c>data</c> node, or null with the reason in
    /// <paramref name="error"/>. The document returns <c>state</c>, the buyer, the cart, payment contingencies
    /// and completed payment info, so a caller reads <c>state</c> first and treats anything other than a
    /// completed state as a non-approval.
    /// </summary>
    public static async Task<(JObject? Data, string Error)> ApproveAsync(
        FlowContext c, JObject variables, CancellationToken ct, string? url = null)
    {
        if (variables?["token"] is null || string.IsNullOrEmpty(variables["token"]!.ToString()))
            return (null, "approve: no token — the approval is keyed by the buyer token and cannot be replayed");

        var options = c.Options("paypal-approve");
        // R1370: the dialect follows the payment. A funding option that carries an encrypted paycode needs the
        // longer document; everything else takes the one this class has always sent.
        var body = EnvelopeFor(variables);

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, url ?? Url, body, "paypal-approve", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "approve: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "approve: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "approve: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "approve: " + ex.GetType().Name);
        }
    }
}
