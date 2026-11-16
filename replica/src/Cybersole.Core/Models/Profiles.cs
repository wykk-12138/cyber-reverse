using Newtonsoft.Json;

namespace Cybersole.Core.Models;

/// <summary>Billing profile: identity + address + payment instrument.</summary>
public sealed class Profile : ObservableObject
{
    private string _name = "Profile 1";
    private string _email = string.Empty;
    private string _username = string.Empty;
    private string _firstName = string.Empty;
    private string _lastName = string.Empty;
    private string _phone = string.Empty;
    private string _address1 = string.Empty;
    private string _address2 = string.Empty;
    private string _city = string.Empty;
    private string _state = string.Empty;
    private string _zip = string.Empty;
    private string _country = "US";
    private string _cardNumber = string.Empty;
    private string _cardExpiry = string.Empty;
    private string _cardCvv = string.Empty;
    private string _cardName = string.Empty;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }

    /// <summary>
    /// The delivery details this profile carries (bound as <c>Delivery</c> on Models.Profile). A profile is what the
    /// checkout form is filled from, and shipping is part of that form.
    /// </summary>
    public string Delivery { get; set; } = string.Empty;
    public string Email { get => _email; set => SetProperty(ref _email, value); }

    /// <summary>
    /// R488: the original's own binding-descriptor table lists <c>Username</c> on <c>Cybersole.Models.Profile</c>
    /// with **both** a Getter and a Setter (12 descriptors total for that type). So the member exists and is
    /// writable — the earlier "no locale key, therefore unobtainable" reading only meant that its *label* was
    /// unknown, not that the field was absent. What it holds is still unverified (behaviour = Unknown).
    /// </summary>
    public string Username { get => _username; set => SetProperty(ref _username, value); }
    public string FirstName { get => _firstName; set => SetProperty(ref _firstName, value); }
    public string LastName { get => _lastName; set => SetProperty(ref _lastName, value); }
    public string Phone { get => _phone; set => SetProperty(ref _phone, value); }
    public string Address1 { get => _address1; set => SetProperty(ref _address1, value); }
    public string Address2 { get => _address2; set => SetProperty(ref _address2, value); }
    public string City { get => _city; set => SetProperty(ref _city, value); }
    public string State { get => _state; set => SetProperty(ref _state, value); }
    public string Zip { get => _zip; set => SetProperty(ref _zip, value); }
    public string Country { get => _country; set => SetProperty(ref _country, value); }
    public string CardNumber { get => _cardNumber; set => SetProperty(ref _cardNumber, value); }
    public string CardExpiry { get => _cardExpiry; set => SetProperty(ref _cardExpiry, value); }
    public string CardCvv { get => _cardCvv; set => SetProperty(ref _cardCvv, value); }

    /// <summary>
    /// R511: the original binds <c>Card</c> on <c>Cybersole.Models.Profile</c> (descriptor table: Getter + Setter),
    /// and it also binds <c>Models.Card</c> with <c>Number</c> / <c>Cvv</c>. So the original's Profile carries a
    /// nested <see cref="Card"/>.
    /// </summary>
    /// <remarks>
    /// <para>
    /// This is a <b>view over the flat fields</b>, not a stored one. R510 looked at the original's New Profile
    /// dialog: card number, MM/YY and CVV are <b>three separate side-by-side inputs</b>, not one nested control.
    /// Storage stays flat so the file keeps matching that shape; this property is what the binding addresses.
    /// </para>
    /// <para>
    /// <c>[JsonIgnore]</c> is deliberate: there is still no <c>profiles.json</c> sample, so whether the original
    /// writes a <c>card</c> object or three flat keys is unobserved. Keeping it out of the file means the replica
    /// does not invent either answer — and the flat keys it does write are the ones the UI edits.
    /// </para>
    /// </remarks>
    [JsonIgnore]
    public Card Card
    {
        get => new()
        {
            Number = CardNumber,
            Cvv = CardCvv,
            Name = CardName,
            Month = CardExpiry.Length >= 2 ? CardExpiry[..2] : string.Empty,
            Year = CardExpiry.Contains('/') ? CardExpiry[(CardExpiry.IndexOf('/') + 1)..] : string.Empty,
        };
        set
        {
            CardNumber = value.Number ?? string.Empty;
            CardCvv = value.Cvv ?? string.Empty;
            CardName = value.Name ?? string.Empty;
            if (!string.IsNullOrEmpty(value.Month) || !string.IsNullOrEmpty(value.Year))
                CardExpiry = $"{value.Month}/{value.Year}";
        }
    }
    public string CardName { get => _cardName; set => SetProperty(ref _cardName, value); }

    /// <summary>Checkout strategy: 3DS / non-3DS / Apple Pay / PayPal.</summary>
    public string CheckoutType { get; set; } = "3DS";
    public bool OneCheckout { get; set; } = true;
    public string? GroupId { get; set; }
    public string? ProxyGroupId { get; set; }

    [JsonIgnore]
    // ── address-form fields recovered from BillingAddressFormViewModel /
    //    ShippingAddressFormViewModel / AddressFormDataModel. The original keeps a full
    //    international address model (JP furigana, PH barangay, EU VAT, UK title).
    public string? Title { get; set; }
    public string? CareOf { get; set; }
    public string? CompanyName { get; set; }
    public string? District { get; set; }
    public string? Region { get; set; }
    public string? StreetNumber { get; set; }
    public string? StreetWithNumber { get; set; }
    public string? StreetSecondLine { get; set; }
    public string? StreetThirdLine { get; set; }
    public string? VatNumber { get; set; }
    public string? Mobile { get; set; }
    public string? MobilePrefix { get; set; }
    public string? PhonePrefix { get; set; }
    public string? JapaneseName { get; set; }
    public string? JapaneseSurname { get; set; }
    public string? FuriganaName { get; set; }
    public string? FuriganaSurname { get; set; }

    public string Display => $"{FirstName} {LastName}".Trim() is { Length: > 0 } n ? n : Name;

    [JsonIgnore]
    public string Last4 => CardNumber.Length >= 4 ? CardNumber[^4..] : string.Empty;

    /// <summary>
    /// A copy of this profile, with a new <see cref="Id"/>.
    /// </summary>
    /// <remarks>
    /// R63: <c>ProfileViews</c> had its own Clone, and it listed thirteen fields by hand:
    /// Name, Email, FirstName, LastName, Address1, City, State, Zip, Country. <see cref="Profile"/>
    /// has thirty-seven. The twenty-four it dropped included CardNumber, CardExpiry, CardCvv and
    /// CardName — so a cloned profile looked complete in the grid and then could not check out,
    /// because it had no payment details.
    ///
    /// A hand-written field list cannot stay correct as the model grows; it fails silently, and the
    /// failure surfaces somewhere else entirely. <c>MemberwiseClone</c> copies every field
    /// including ones added later. Every non-Id member here is a string, a bool or an enum, so
    /// there is no reference to share and nothing that needs a deep copy.
    /// </remarks>
    public Profile Clone()
    {
        var copy = (Profile)MemberwiseClone();
        copy.Id = Guid.NewGuid().ToString("N")[..8];
        return copy;
    }
}

public sealed class ProfileGroup : ObservableObject
{
    private string _name = "Group 1";
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public int Order { get; set; }
    public List<Profile> Profiles { get; set; } = new();
}

/// <summary>Custom (user defined) store entry from settings.customStores.</summary>
/// <summary>
/// A named set of stores (Cybersole.Ui.Views.Utilities + StoreGroupModal). Tasks and
/// monitors pick a group instead of listing every store by hand.
/// </summary>
public sealed class StoreGroup : ObservableObject
{
    private string _name = "Group 1";
    private bool _enabled = true;

    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public bool Enabled { get => _enabled; set => SetProperty(ref _enabled, value); }

    /// <summary>Module ids (Cybersole.Http.Stores.IStoreModule.Id) in this group.</summary>
    public List<string> Stores { get; set; } = new();

    /// <summary>
    /// Which configured Cloudflare provider this group uses. The live Cloudflare Providers
    /// page says "pick one per task group", so the choice belongs here rather than globally.
    /// </summary>
    public string? CloudflareProviderId { get; set; }

    /// <summary>Which configured captcha provider this group uses, from the group's Captcha tab.</summary>
    public string? CaptchaProviderId { get; set; }

    public override string ToString() => $"{Name} ({Stores.Count})";
}

public sealed class CustomStore
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];

    /// <summary>Derived from the shop when the preset is added; the dialog only asks for a URL.</summary>
    public string Name { get; set; } = string.Empty;

    public string Url { get; set; } = string.Empty;

    /// <summary>Shop currency, read from the store once the preset is added.</summary>
    public string Currency { get; set; } = "USD";

    public string? Type { get; set; }
}

/// <summary>Notification channel options (settings.notificationOptions).</summary>
public sealed class NotificationOptions : ObservableObject
{
    private bool _enabled = true;
    private bool _centre = true;
    private bool _desktop = true;
    private bool _sound = true;
    private string _path = string.Empty;

    public bool Enabled { get => _enabled; set => SetProperty(ref _enabled, value); }
    public bool Centre { get => _centre; set => SetProperty(ref _centre, value); }
    public bool Desktop { get => _desktop; set => SetProperty(ref _desktop, value); }
    public bool Sound { get => _sound; set => SetProperty(ref _sound, value); }

    /// <summary>
    /// The same switch under the original's binding name (analysis/xaml_bindings.json binds <c>EnableSound</c>).
    /// Kept as an alias rather than a second field, so there is one source of truth for "play a sound".
    /// </summary>
    public bool EnableSound { get => Sound; set => Sound = value; }
    public string Path { get => _path; set => SetProperty(ref _path, value); }

    /// <summary>
    /// Which notification category these options configure (bound as <c>Name</c>, R362) — the five the notifications page
    /// tabs between: Checkout, Decline, Captcha, Smart Actions, Other.
    /// </summary>
    public string Name { get; set; } = string.Empty;
}

/// <summary>Keyboard chord (settings.keyBinds).</summary>
public sealed class KeyBind
{
    public int Key { get; set; }
    public int Modifiers { get; set; }
}

/// <summary>Monitor filter switches (settings.monitorFilters).</summary>
public sealed class MonitorFilters
{
    public bool Shopify { get; set; } = true;
    public bool Nike { get; set; } = true;
    public bool Footsites { get; set; } = true;
    public bool Supreme { get; set; } = true;
    public bool OffSpringOrOffice { get; set; } = true;
    public bool PopMart { get; set; } = true;
    public bool CheckoutFeed { get; set; } = true;
}

/// <summary>Concurrency policy (settings.concurrency).</summary>
public sealed class ConcurrencySettings
{
    public ConcurrencyMode Mode { get; set; } = ConcurrencyMode.Both;
    public int Maximum { get; set; } = 3;
    public double Ratio { get; set; } = 0.1;
}
