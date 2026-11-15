using System.Text.Json;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The raffle / sale-registration surface, read out of the 5.18.32 image in R99.
///
/// <para>
/// The replica had no raffle support beyond a SuperSwipe module. The image carries a whole draw
/// vocabulary, including the three pieces that make a Demandware draw work:
/// </para>
///
/// <code>
/// /pages/raffle?pro…                                  the entry page
/// &lt;script id="panagora-raffle-data"[^&gt;]*&gt;(.*?)&lt;/script&gt;   the data extractor, verbatim
/// .raffle-data[data-id]                               the DOM selector fallback
/// /api/raffle-sig                                     the signature endpoint
/// SaleRegistration-Config / SaleRegistration-SignupSubmit   the two Demandware controllers
/// /Cart-CartDrawBody                                  the draw cart fragment
/// Already Entered Draw                                the duplicate-entry status
/// </code>
///
/// <para>
/// The extractor is the image's own regex, character for character. It matters that this is not
/// "parse the page somehow": the raffle data lives in a script tag with a fixed id, and a different
/// regex finds a different document.
/// </para>
/// </summary>
public static class DemandwareRaffle
{
    /// <summary>The entry page path, verbatim (the image's literal is cut off at <c>?pro</c>).</summary>
    public const string EntryPage = "/pages/raffle";

    /// <summary>The data extractor, verbatim from the image.</summary>
    public const string DataPattern =
        "<script id=\"panagora-raffle-data\"[^>]*>(.*?)</script>";

    /// <summary>The DOM selector the image also carries, for a page that renders the data inline.</summary>
    public const string DataSelector = ".raffle-data[data-id]";

    /// <summary>The signature endpoint.</summary>
    public const string Signature = "/api/raffle-sig";

    /// <summary>The status a duplicate entry comes back with.</summary>
    public const string AlreadyEntered = "Already Entered Draw";

    /// <summary>The draw cart fragment controller.</summary>
    public const string DrawCart = "Cart-CartDrawBody";

    /// <summary>
    /// Pulls the raffle JSON out of a page. Returns null when the page has no raffle script — which
    /// is the normal answer for a store that is not running a draw, and must not be an error.
    /// </summary>
    public static string? ExtractData(string? html)
    {
        if (string.IsNullOrEmpty(html)) return null;

        var match = System.Text.RegularExpressions.Regex.Match(
            html, DataPattern,
            System.Text.RegularExpressions.RegexOptions.Singleline |
            System.Text.RegularExpressions.RegexOptions.IgnoreCase);

        if (!match.Success) return null;

        var payload = match.Groups[1].Value.Trim();
        return payload.Length == 0 ? null : payload;
    }

    /// <summary>
    /// The raffle id from the extracted payload, if it has one. Demandware puts it on the wrapper
    /// (<c>data-id</c>) or inside the JSON; both shapes are accepted.
    /// </summary>
    public static string? ExtractId(string? html)
    {
        var payload = ExtractData(html);
        if (payload is null) return null;

        try
        {
            using var doc = JsonDocument.Parse(payload);
            foreach (var name in new[] { "id", "raffleId", "dataId" })
                if (doc.RootElement.TryGetProperty(name, out var value))
                {
                    var text = value.ValueKind == JsonValueKind.String ? value.GetString() : value.ToString();
                    if (!string.IsNullOrWhiteSpace(text)) return text;
                }
        }
        catch (JsonException)
        {
            // not JSON — fall through to the attribute form
        }

        var attribute = System.Text.RegularExpressions.Regex.Match(
            html!, "data-id=\"([^\"]+)\"",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase);

        return attribute.Success ? attribute.Groups[1].Value : null;
    }

    /// <summary>True when the response says this profile already entered the draw.</summary>
    public static bool IsAlreadyEntered(string? body) =>
        !string.IsNullOrEmpty(body) &&
        body.Contains(AlreadyEntered, StringComparison.OrdinalIgnoreCase);
}
