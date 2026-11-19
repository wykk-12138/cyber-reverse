using System;
using System.Globalization;

namespace Cybersole.Stores;

/// <summary>
/// Waitwhile — the queue/waitlist service the original talks to for an in-store slot.
///
/// <para>
/// <b>Observed</b> in four functions, each reached from a frozen literal:
/// <c>https://api.waitwhile.com/v2/public/data-fields/</c> (0x147055450, referenced by <c>sub_140B76CF0</c>),
/// <c>https://api.waitwhile.com/v2/public/locations/</c> (0x1470554C8, <c>sub_140B73520</c> and
/// <c>sub_140B76CF0</c>), and <c>https://api.waitwhile.com/v2/public/visits/</c> (0x147055540,
/// <c>sub_140B77010</c> and <c>sub_140B77860</c>). The visits function additionally carries the slot query:
/// <c>/first-available-slots?fromDate=</c> (0x146AB4E10), <c>T00:00&amp;toDate=</c> (0x146EAF698),
/// <c>T00:00&amp;maxNumSlots=150</c> (0x146EAF650), the format string <c>yyyy-MM-dd</c> (0x14718CF50) and the report
/// line <c>Find slot</c> (0x146D90D70).
/// </para>
///
/// <para>
/// <b>Inference</b>: the day is formatted with <c>yyyy-MM-dd</c> and the literal <c>T00:00</c> is appended to each
/// bound, so both bounds are start-of-day; <c>maxNumSlots</c> is fixed at 150 rather than passed in, because 150 is
/// part of the literal rather than a value the function formats.
/// </para>
///
/// <para>
/// <b>Unknown</b>: which location id goes into the slot path, and what a slot response looks like — the image
/// carries the request shape but no response field names, and those come from the account behind the queue.
/// </para>
/// </summary>
public static class WaitwhileQueue
{
    public const string VisitsHost = "https://api.waitwhile.com/v2/public/visits/";

    public const string LocationsHost = "https://api.waitwhile.com/v2/public/locations/";

    public const string DataFieldsHost = "https://api.waitwhile.com/v2/public/data-fields/";

    /// <summary>The image's own date format for the two bounds (0x14718CF50).</summary>
    public const string DateFormat = "yyyy-MM-dd";

    /// <summary>The fixed slot ceiling, which is part of the literal and therefore not a caller parameter.</summary>
    public const int MaxSlots = 150;

    /// <summary>
    /// <c>{VisitsHost}{locationId}/first-available-slots?fromDate=&lt;from&gt;T00:00&amp;toDate=&lt;to&gt;T00:00&amp;maxNumSlots=150</c>
    /// </summary>
    public static string FirstAvailableSlotsUrl(string locationId, DateTime from, DateTime to)
    {
        return VisitsHost + Uri.EscapeDataString(locationId ?? string.Empty)
            + "/first-available-slots?fromDate=" + Day(from)
            + "&toDate=" + Day(to)
            + "&maxNumSlots=" + MaxSlots.ToString(CultureInfo.InvariantCulture);
    }

    /// <summary>One bound, formatted the way the image formats it and given the literal start-of-day suffix.</summary>
    public static string Day(DateTime value) =>
        value.ToString(DateFormat, CultureInfo.InvariantCulture) + "T00:00";

    /// <summary>
    /// The cache-busting query the location lookup appends (0x146B277D8, <c>"?_="</c>).
    ///
    /// <para>
    /// <b>Observed</b> in <c>sub_140B73520</c> (367 bytes), whose whole constant set is that fragment and
    /// <see cref="LocationsHost"/>, and it is the only function that references the location host on its own.
    /// </para>
    ///
    /// <para>
    /// <b>Unknown</b>: what the value after <c>?_=</c> is. The literal stops at the equals sign, so the value is
    /// computed rather than concatenated from a second literal, and the decompiled constant set cannot say whether it
    /// is a tick count, an epoch second or something else. The builder therefore takes it as a parameter.
    /// </para>
    /// </summary>
    public const string CacheBusterParam = "?_=";

    /// <summary><c>{LocationsHost}{locationId}?_=&lt;cacheBuster&gt;</c> (sub_140B73520).</summary>
    public static string LocationUrl(string locationId, string cacheBuster) =>
        LocationsHost + Uri.EscapeDataString(locationId ?? string.Empty)
        + CacheBusterParam + Uri.EscapeDataString(cacheBuster ?? string.Empty);

    /// <summary>
    /// <c>sub_140B76CF0</c> (721 bytes) resolves a location and then asks for that location's data fields, which is
    /// why it carries both hosts plus the report line <c>Find location</c> (0x146D90D10). The order is the
    /// observation; what the field response contains is <b>Unknown</b> — the image keeps the request and not the
    /// schema.
    /// </summary>
    public static string DataFieldsUrl(string locationId) =>
        DataFieldsHost + Uri.EscapeDataString(locationId ?? string.Empty);
}
