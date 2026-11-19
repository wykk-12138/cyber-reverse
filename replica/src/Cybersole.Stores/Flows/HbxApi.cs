using System;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The HBX API strings the image actually carries (R1258, from the full string dump).
///
/// <para>
/// <b>Observed</b>: the image holds the host-qualified cart endpoint twice, once with the trailing slash and once
/// without — <c>https://hbx.com/api/v1/carts</c> and <c>https://hbx.com/api/v1/carts/</c> — beside the bare token
/// <c>api/v1/carts</c> and a v2 shape the replica does not use: <c>api/v2/carts/contents/</c>.
/// </para>
///
/// <para>
/// <b>Inference</b>: because the host and the path appear together in one literal, the replica's habit of taking the
/// origin from the page and appending <c>/api/v1/carts</c> reproduces the same address the image writes out in full.
/// That makes <see cref="HbxFlow"/>'s cart endpoints assembled-from-attested rather than invented, which is the same
/// standing as the Magento basket path from R1251.
/// </para>
///
/// <para>
/// <b>Not observed</b>: <c>/api/v2/shop/countries</c> has no hit and no neighbour — not even the fragment
/// <c>shop/countries</c> appears — so that call keeps its <c>inferred</c> marker at the call site. The v2 family the
/// image does carry is about cart contents, not about shop metadata.
/// </para>
///
/// <para>
/// <b>Unknown</b>: what the contents endpoint answers and which step would read it. It is exposed here because the
/// literal is attested; it is not wired to any step on the strength of a path alone.
/// </para>
/// </summary>
public static class HbxApi
{
    /// <summary>Host-qualified, no trailing slash (the form the image writes out).</summary>
    public const string CartsAbsolute = "https://hbx.com/api/v1/carts";

    /// <summary>The same endpoint with the trailing slash, which the image carries beside it.</summary>
    public const string CartsAbsoluteSlash = "https://hbx.com/api/v1/carts/";

    /// <summary>The bare token, for callers that prepend their own origin.</summary>
    public const string CartsToken = "api/v1/carts";

    /// <summary>The v2 shape the image carries and the replica does not use.</summary>
    public const string CartsContentsV2 = "api/v2/carts/contents/";

    /// <summary>The address the replicated call actually produces, given an origin.</summary>
    public static string CartsUrl(string origin) =>
        (origin ?? string.Empty).TrimEnd('/') + "/" + CartsToken;
}
