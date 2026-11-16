using Cybersole.Core.Models;

namespace Cybersole.Http.Stores;

/// <summary>
/// Turns a billing profile + store account into the field map a checkout form expects.
/// The store modules use this instead of each re-implementing address/card mapping.
/// </summary>
public static class CheckoutFormBuilder
{
    public static Dictionary<string, string> Build(Profile? profile, Account? account, string? size = null)
    {
        var fields = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        // identity: the account's email wins, the profile is the billing fallback
        var email = FirstNonEmpty(account?.Email, profile?.Email);
        if (email.Length > 0) fields["email"] = email;

        if (account is not null && !string.IsNullOrEmpty(account.Password))
            fields["password"] = account.Password;

        if (profile is not null)
        {
            AddIfSet(fields, "firstName", profile.FirstName);
            AddIfSet(fields, "lastName", profile.LastName);
            AddIfSet(fields, "phone", profile.Phone);
            AddIfSet(fields, "address1", profile.Address1);
            AddIfSet(fields, "address2", profile.Address2);
            AddIfSet(fields, "city", profile.City);
            AddIfSet(fields, "state", profile.State);
            AddIfSet(fields, "zip", profile.Zip);
            AddIfSet(fields, "country", profile.Country);

            var cardNumber = NormaliseCardNumber(profile.CardNumber);
            if (cardNumber.Length > 0)
            {
                fields["cardNumber"] = cardNumber;
                fields["cardExpiry"] = NormaliseExpiry(profile.CardExpiry);
                AddIfSet(fields, "cardCvv", profile.CardCvv);
                fields["cardName"] = FirstNonEmpty(profile.CardName,
                    $"{profile.FirstName} {profile.LastName}".Trim());
            }
        }

        if (!string.IsNullOrWhiteSpace(size)) fields["size"] = size.Trim();

        return fields;
    }

    /// <summary>Strips spaces/dashes so gateways stop rejecting formatted numbers.</summary>
    public static string NormaliseCardNumber(string? value)
        => string.IsNullOrWhiteSpace(value)
            ? string.Empty
            : new string(value.Where(char.IsDigit).ToArray());

    /// <summary>Accepts "1/28", "01/2028", "0128" and emits MM/YY.</summary>
    public static string NormaliseExpiry(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return string.Empty;

        var digits = new string(value.Where(char.IsDigit).ToArray());
        if (digits.Length == 3) digits = "0" + digits;              // 128 -> 0128
        if (digits.Length >= 4)
        {
            var month = digits[..2];
            var yearPart = digits[2..];
            // tolerate MMYY, MMYYYY and 4-digit years with a 1-digit month
            var year = yearPart.Length >= 4 ? yearPart[^2..] : yearPart;
            return $"{month}/{year}";
        }

        return value.Trim();
    }

    private static string FirstNonEmpty(params string?[] values)
        => values.FirstOrDefault(v => !string.IsNullOrWhiteSpace(v))?.Trim() ?? string.Empty;

    private static void AddIfSet(Dictionary<string, string> fields, string key, string? value)
    {
        if (!string.IsNullOrWhiteSpace(value)) fields[key] = value.Trim();
    }
}
