"""Write replica/src/Cybersole.Stores/Payments/SquareBrowserData.cs from the image bytes.

The template is 1124 bytes of JSON and typing it by hand is exactly how a replica ends up with a fingerprint
that differs from the image's in one font name nobody notices. So the file is generated from the bytes at
0x143385527, and the SansUa variant is not stored at all: it is derived by removing the first member, and a
test asserts that derivation reproduces the image's second template (1102 bytes, 22 shorter) character for
character. Storing both would let them drift; deriving proves the relationship.

The prose around the literal is written here rather than generated, so this script is run once and the file
thereafter is ordinary source.
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from extract_square_fingerprint import BASE, SPAN, cut_object, find_all, read  # noqa: E402

OUT = 'replica/src/Cybersole.Stores/Payments/SquareBrowserData.cs'

base, blob = read()
sites = find_all(blob, b'{"user_agent":"__UA__"')
if len(sites) != 1:
    print('expected exactly one with-UA template, found %d' % len(sites))
    sys.exit(1)
raw = cut_object(blob, sites[0])
if raw is None:
    print('could not cut the object')
    sys.exit(1)

text = raw.decode('utf-8')
# Verbatim literals cannot contain a run of three quotes; the JSON has none, and this is the check.
if '"""' in text:
    print('the template contains a triple quote and cannot be a verbatim literal')
    sys.exit(1)

template = '"""' + text + '"""'

SOURCE = '''using System;
using System.Collections.Generic;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Square's Web Payments device fingerprint — the <c>browserData</c> a <c>card</c> object carries when the
/// hosted SDK tokenises a card.
///
/// <para>
/// <b>Observed</b>: the image holds two copies of this object side by side in the store class's metadata
/// (0x143385527 and 0x1433859A0) beside the names <c>ComponentsV1</c>, <c>ComponentsV1SansUa</c>,
/// <c>SquareSdkVersion</c> = <c>1.83.9</c>, <c>SquareLocationId</c> = <c>L0NR598Z0FFW5</c>,
/// <c>_cardNonce</c> and <c>_ccType</c>. The first copy is %(length)d bytes with a literal
/// <c>__UA__</c> in the <c>user_agent</c> slot; the second is %(sans_length)d bytes and is the same object
/// with that one member removed — every other member is identical, which is why the two names differ only
/// by "SansUa".
/// </para>
///
/// <para>
/// The values are the store owner's tested device, not the user's: a 5120x1440 screen with 5120x1392
/// available, timezone offset -120, <c>Win32</c>, five PDF plugins, thirty-five fonts, no adblock and
/// <c>touch_support</c> <c>[10,false,false]</c>. A randomising fingerprint would be a different claim
/// from the one the image makes, so this reproduces the frozen one.
/// </para>
///
/// <para>
/// <b>Where it belongs</b>: this is the <em>SDK</em> payload, not the server-side
/// <c>/v2/card-nonce</c> HTTP body <see cref="SquareGateway.TokenizeAsync"/> posts. Modelling it here does
/// not change that request — saying otherwise would be a guess about which surface reads it.
/// </para>
/// </summary>
public static class SquareBrowserData
{
    /// <summary>The placeholder the SDK fills with the browser's own agent string.</summary>
    public const string UserAgentPlaceholder = "__UA__";

    /// <summary><c>SquareSdkVersion</c> as the image spells it.</summary>
    public const string SdkVersion = "1.83.9";

    /// <summary>The component set the two template names refer to.</summary>
    public const string ComponentSet = "ComponentsV1";

    /// <summary>
    /// <c>SquareLocationId</c> for the store the fingerprint was recorded on. A caller with its own store
    /// supplies one through <c>square.locationId</c>; this is the image's.
    /// </summary>
    public const string DefaultLocationId = "L0NR598Z0FFW5";

    /// <summary>The member the SansUa variant drops, exactly as it appears in the template.</summary>
    private const string UserAgentMember = "\\"user_agent\\":\\"__UA__\\",";

    /// <summary>
    /// The full fingerprint, byte for byte from 0x143385527, with <c>__UA__</c> left in place so the
    /// placeholder is visible rather than silently empty.
    /// </summary>
    public const string Template = %(template)s;

    /// <summary>
    /// The <c>ComponentsV1SansUa</c> form: the same object without the <c>user_agent</c> member. Derived
    /// rather than stored, so the two can never drift; the test asserts the derivation reproduces the
    /// image's second copy exactly, including its %(sans_length)d-byte length.
    /// </summary>
    public static string WithoutUserAgent() => Template.Replace(UserAgentMember, string.Empty, StringComparison.Ordinal);

    /// <summary>
    /// The fingerprint with the caller's agent string in place of the placeholder, or the SansUa form when
    /// there is no agent string to supply — which is the case the second template exists for.
    /// </summary>
    public static string Build(string? userAgent)
    {
        if (string.IsNullOrWhiteSpace(userAgent)) return WithoutUserAgent();
        return Template.Replace(UserAgentPlaceholder, Escape(userAgent!), StringComparison.Ordinal);
    }

    /// <summary>
    /// A JSON string escape for the agent value. The agent goes inside a string literal that is itself
    /// inside JSON, so the only characters that can break it are the quote and the backslash.
    /// </summary>
    private static string Escape(string value) =>
        value.Replace("\\\\", "\\\\\\\\", StringComparison.Ordinal).Replace("\\"", "\\\\\\"", StringComparison.Ordinal);

    /// <summary>The fingerprint's own facts, for anything that has to compare against them.</summary>
    public static IReadOnlyDictionary<string, string> Recorded { get; } = new Dictionary<string, string>
    {
        ["resolution"] = "5120x1440",
        ["available_resolution"] = "5120x1392",
        ["timezone_offset"] = "-120",
        ["navigator_platform"] = "Win32",
        ["plugins"] = "5",
        ["fonts"] = "35",
        ["adblock"] = "false",
        ["touch_support"] = "10,false,false",
    };
}
''' % {'length': len(raw), 'sans_length': len(raw) - 22, 'template': template}

io.open(OUT, 'w', encoding='utf-8', newline='').write(SOURCE)
print('wrote %s (%d bytes of source, template %d bytes)' % (OUT, len(SOURCE), len(raw)))
