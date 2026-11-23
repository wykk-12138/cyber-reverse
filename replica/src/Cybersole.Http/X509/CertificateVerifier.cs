using System.Buffers.Binary;
using System.Net;
using Cybersole.Http.Crypto;

namespace Cybersole.Http.X509;

/// <summary>
/// Exception thrown when X.509 chain, validity, constraint, or hostname verification fails.
/// </summary>
public class CertificateValidationException : Exception
{
    public CertificateValidationException(string message)
        : base(message)
    {
    }

    public CertificateValidationException(string message, Exception? innerException)
        : base(message, innerException)
    {
    }
}

/// <summary>
/// Exception thrown when a verified certificate chain fails configured SPKI SHA-256 pins.
/// </summary>
public sealed class BadPinException : CertificateValidationException
{
    public BadPinException(string message)
        : base(message)
    {
    }

    public BadPinException(string message, Exception? innerException)
        : base(message, innerException)
    {
    }
}

/// <summary>
/// SPKI SHA-256 certificate pinner matching exact hosts and wildcard host patterns (e.g. <c>*.example.com</c>).
/// </summary>
public sealed class CertificatePinner
{
    private readonly Dictionary<string, List<byte[]>> _pinsByHost = new(StringComparer.OrdinalIgnoreCase);

    public void AddPin(string hostPattern, string pin)
    {
        var key = NormalizeHostPattern(hostPattern);
        var hash = ParsePinSha256(pin);

        if (!_pinsByHost.TryGetValue(key, out var list))
        {
            list = new List<byte[]>();
            _pinsByHost[key] = list;
        }
        list.Add(hash);
    }

    public void AddPins(string hostPattern, IEnumerable<string> pins)
    {
        ArgumentNullException.ThrowIfNull(pins);
        foreach (var pin in pins)
            AddPin(hostPattern, pin);
    }

    public bool HasPinsForHost(string host)
    {
        if (string.IsNullOrWhiteSpace(host))
            return false;
        return TryResolvePins(host, out _);
    }

    public void VerifyPins(string host, IReadOnlyList<DerCertificate> verifiedChain)
    {
        ArgumentNullException.ThrowIfNull(verifiedChain);
        if (string.IsNullOrWhiteSpace(host))
            return;

        if (!TryResolvePins(host, out var expectedHashes) || expectedHashes.Count == 0)
            return;

        for (var i = 0; i < verifiedChain.Count; i++)
        {
            var spkiHash = verifiedChain[i].SpkiSha256;
            for (var j = 0; j < expectedHashes.Count; j++)
            {
                if (ConstantTime.Equals(spkiHash, expectedHashes[j]))
                    return;
            }
        }

        var foundPins = new string[verifiedChain.Count];
        for (var i = 0; i < verifiedChain.Count; i++)
            foundPins[i] = "sha256/" + verifiedChain[i].PinSha256Base64;

        throw new BadPinException($"bad ssl pin detected, found pins: [{string.Join(" ", foundPins)}]");
    }

    private bool TryResolvePins(string host, out List<byte[]> pins)
    {
        var normalized = NormalizeHostName(host);
        if (_pinsByHost.TryGetValue(normalized, out pins!))
            return true;

        var parts = normalized.Split('.');
        for (var i = 1; i < parts.Length - 1; i++)
        {
            var wildcardSuffix = "." + string.Join('.', parts, i, parts.Length - i);
            if (_pinsByHost.TryGetValue(wildcardSuffix, out pins!))
                return true;
        }

        pins = null!;
        return false;
    }

    private static string NormalizeHostPattern(string hostPattern)
    {
        if (string.IsNullOrWhiteSpace(hostPattern))
            throw new ArgumentException("Host pattern cannot be empty.", nameof(hostPattern));

        var trimmed = hostPattern.Trim().TrimEnd('.').ToLowerInvariant();
        if (trimmed.StartsWith("*.", StringComparison.Ordinal))
        {
            var suffix = trimmed.Substring(1); // keep leading '.' for subdomain lookup
            if (suffix.Length <= 1)
                throw new ArgumentException($"Invalid wildcard host pattern: '{hostPattern}'.", nameof(hostPattern));
            return suffix;
        }

        return trimmed;
    }

    private static string NormalizeHostName(string host)
    {
        var trimmed = host.Trim();
        if (trimmed.Length > 1 && trimmed[^1] == '.')
            trimmed = trimmed[..^1];
        return trimmed.ToLowerInvariant();
    }

    private static byte[] ParsePinSha256(string pin)
    {
        if (string.IsNullOrWhiteSpace(pin))
            throw new ArgumentException("Pin string cannot be empty.", nameof(pin));

        var s = pin.Trim();
        if (s.StartsWith("sha256/", StringComparison.OrdinalIgnoreCase))
            s = s.Substring("sha256/".Length);
        else if (s.StartsWith("pin-sha256=", StringComparison.OrdinalIgnoreCase))
            s = s.Substring("pin-sha256=".Length).Trim('"');

        byte[] decoded;
        try
        {
            decoded = Convert.FromBase64String(s);
        }
        catch (FormatException ex)
        {
            throw new ArgumentException($"Invalid Base64 SHA-256 pin: '{pin}'.", nameof(pin), ex);
        }

        if (decoded.Length != 32)
            throw new ArgumentException($"SHA-256 pin must decode to 32 bytes (got {decoded.Length}).", nameof(pin));

        return decoded;
    }
}

/// <summary>
/// Pure managed trusted root certificate database loaded directly from the embedded
/// <c>Cybersole.Http.X509.RootCertificates.bin</c> bundle (121 roots) via <see cref="DerCertificate"/>.
/// </summary>
public sealed class RootCertificateDatabase
{
    private static readonly Lazy<RootCertificateDatabase> SharedInstance =
        new(LoadEmbedded, isThreadSafe: true);

    private readonly List<DerCertificate> _certificates = new();
    private readonly HashSet<ReadOnlyMemory<byte>> _seenDer = new(ReadOnlyMemoryByteComparer.Instance);
    private readonly Dictionary<ReadOnlyMemory<byte>, List<DerCertificate>> _bySubjectRaw = new(ReadOnlyMemoryByteComparer.Instance);
    private readonly Dictionary<ReadOnlyMemory<byte>, List<DerCertificate>> _bySubjectKeyId = new(ReadOnlyMemoryByteComparer.Instance);

    public static RootCertificateDatabase Default => SharedInstance.Value;
    public static RootCertificateDatabase Shared => SharedInstance.Value;

    public int Count => _certificates.Count;
    public IReadOnlyList<DerCertificate> Certificates => _certificates;

    public void Add(DerCertificate certificate)
    {
        ArgumentNullException.ThrowIfNull(certificate);
        if (!_seenDer.Add(certificate.RawDer))
            return;

        _certificates.Add(certificate);

        if (!_bySubjectRaw.TryGetValue(certificate.SubjectRaw, out var subjectList))
        {
            subjectList = new List<DerCertificate>();
            _bySubjectRaw[certificate.SubjectRaw] = subjectList;
        }
        subjectList.Add(certificate);

        if (certificate.SubjectKeyId is { Length: > 0 } ski)
        {
            ReadOnlyMemory<byte> skiMem = ski;
            if (!_bySubjectKeyId.TryGetValue(skiMem, out var skiList))
            {
                skiList = new List<DerCertificate>();
                _bySubjectKeyId[skiMem] = skiList;
            }
            skiList.Add(certificate);
        }
    }

    public void AddDer(ReadOnlySpan<byte> der) => Add(DerCertificate.Parse(der));

    public bool Contains(DerCertificate certificate)
    {
        ArgumentNullException.ThrowIfNull(certificate);
        return _seenDer.Contains(certificate.RawDer);
    }

    public IReadOnlyList<DerCertificate> FindBySubjectRaw(ReadOnlyMemory<byte> subjectRaw) =>
        _bySubjectRaw.TryGetValue(subjectRaw, out var list) ? list : Array.Empty<DerCertificate>();

    public IReadOnlyList<DerCertificate> FindBySubjectRaw(ReadOnlySpan<byte> subjectRaw) =>
        FindBySubjectRaw(subjectRaw.ToArray().AsMemory());

    public static RootCertificateDatabase LoadFromBundleStream(Stream stream)
    {
        ArgumentNullException.ThrowIfNull(stream);
        var db = new RootCertificateDatabase();
        Span<byte> lenBuf = stackalloc byte[4];
        while (ReadExact(stream, lenBuf))
        {
            var len = BinaryPrimitives.ReadUInt32BigEndian(lenBuf);
            if (len == 0 || len > 16 * 1024 * 1024)
                throw new InvalidDataException($"Invalid X.509 DER record length: {len}");

            var der = new byte[len];
            if (!ReadExact(stream, der))
                throw new EndOfStreamException("Truncated DER certificate record in root bundle.");

            db.Add(DerCertificate.Parse(der));
        }
        return db;
    }

    public static RootCertificateDatabase LoadEmbedded()
    {
        var asm = typeof(RootCertificateDatabase).Assembly;
        using var stream = asm.GetManifestResourceStream(RootCertificateStore.ResourceName);
        if (stream is null)
            throw new InvalidOperationException($"embedded resource {RootCertificateStore.ResourceName} is missing");

        return LoadFromBundleStream(stream);
    }

    private static bool ReadExact(Stream stream, Span<byte> target)
    {
        var offset = 0;
        while (offset < target.Length)
        {
            var read = stream.Read(target.Slice(offset));
            if (read == 0)
                return offset == 0 ? false : throw new EndOfStreamException();
            offset += read;
        }
        return true;
    }
}

internal sealed class ReadOnlyMemoryByteComparer : IEqualityComparer<ReadOnlyMemory<byte>>
{
    public static readonly ReadOnlyMemoryByteComparer Instance = new();

    public bool Equals(ReadOnlyMemory<byte> x, ReadOnlyMemory<byte> y) => x.Span.SequenceEqual(y.Span);

    public int GetHashCode(ReadOnlyMemory<byte> obj)
    {
        var hc = new HashCode();
        hc.AddBytes(obj.Span);
        return hc.ToHashCode();
    }
}

/// <summary>
/// Options controlling <see cref="CertificateVerifier.VerifyChain"/>.
/// </summary>
public sealed class CertificateVerifyOptions
{
    public bool InsecureSkipVerify { get; set; }
    public DateTimeOffset? VerificationTime { get; set; }
    public RootCertificateDatabase? CustomRoots { get; set; }
    public bool UseEmbeddedDefaultRoots { get; set; } = true;
    public CertificatePinner? Pinner { get; set; }
    public int MaxChainLength { get; set; } = 10;
    public int MaxSignatureChecks { get; set; } = 100;
    public bool AllowSha1 { get; set; }
}

/// <summary>
/// Pure managed RFC 5280 / RFC 6125 TLS X.509 certificate chain verifier.
/// Uses <see cref="RootCertificateDatabase"/> and pure managed ASN.1/crypto primitives exclusively.
/// </summary>
public static class CertificateVerifier
{
    private const string EkuServerAuth = "1.3.6.1.5.5.7.3.1";
    private const string EkuAny = "2.5.29.37.0";
    private const string EkuNetscapeSgc = "2.16.840.1.113730.4.1";
    private const string EkuMicrosoftSgc = "1.3.6.1.4.1.311.10.3.3";

    public static IReadOnlyList<DerCertificate> VerifyChain(
        IReadOnlyList<byte[]> derChain,
        string? targetHost,
        CertificateVerifyOptions? options = null)
    {
        options ??= new CertificateVerifyOptions();

        if (options.MaxChainLength < 1)
            throw new ArgumentOutOfRangeException(nameof(options), "MaxChainLength must be >= 1.");
        if (options.MaxSignatureChecks < 1)
            throw new ArgumentOutOfRangeException(nameof(options), "MaxSignatureChecks must be >= 1.");

        if (derChain is null || derChain.Count == 0)
            throw new CertificateValidationException("x509: no certificates presented");

        var parsedPresented = new List<DerCertificate>(derChain.Count);
        try
        {
            for (var i = 0; i < derChain.Count; i++)
            {
                if (derChain[i] is null)
                    throw new CertificateValidationException($"x509: certificate at index {i} is null");
                parsedPresented.Add(DerCertificate.Parse(derChain[i]));
            }
        }
        catch (FormatException ex)
        {
            throw new CertificateValidationException($"x509: failed to parse DER certificate: {ex.Message}", ex);
        }

        var leaf = parsedPresented[0];

        if (options.InsecureSkipVerify)
        {
            if (options.Pinner is not null && !string.IsNullOrWhiteSpace(targetHost))
                options.Pinner.VerifyPins(targetHost, parsedPresented);
            return parsedPresented;
        }

        var now = options.VerificationTime ?? DateTimeOffset.UtcNow;

        if (leaf.UnhandledCriticalExtensions.Count > 0)
        {
            throw new CertificateValidationException(
                $"x509: certificate '{leaf.SubjectText}' contains unhandled critical extension(s) ({string.Join(", ", leaf.UnhandledCriticalExtensions)})");
        }

        ValidateValidityWindow(leaf, now);

        if (!HasCompatibleServerAuthEku(leaf))
        {
            throw new CertificateValidationException(
                $"x509: certificate '{leaf.SubjectText}' specifies an incompatible key usage (no serverAuth)");
        }

        if (!string.IsNullOrEmpty(targetHost))
            VerifyHostname(leaf, targetHost);

        if (IsTrustedRoot(leaf, options))
        {
            var selfChain = new[] { leaf };
            if (options.Pinner is not null && !string.IsNullOrWhiteSpace(targetHost))
                options.Pinner.VerifyPins(targetHost, selfChain);
            return selfChain;
        }

        var intermediates = new List<DerCertificate>(Math.Max(0, parsedPresented.Count - 1));
        var seenIntermediateDer = new HashSet<ReadOnlyMemory<byte>>(ReadOnlyMemoryByteComparer.Instance) { leaf.RawDer };
        for (var i = 1; i < parsedPresented.Count; i++)
        {
            var candidate = parsedPresented[i];
            if (!IsTrustedRoot(candidate, options) && seenIntermediateDer.Add(candidate.RawDer))
                intermediates.Add(candidate);
        }

        var chain = new List<DerCertificate>(Math.Min(options.MaxChainLength, 10)) { leaf };
        var signatureChecks = 0;
        string? lastFailure = null;

        if (!TryBuildChain(chain, intermediates, targetHost, options, now, ref signatureChecks, ref lastFailure))
            throw new CertificateValidationException(lastFailure ?? $"x509: certificate signed by unknown authority ('{leaf.SubjectText}')");

        var verifiedChain = chain.ToArray();
        if (options.Pinner is not null && !string.IsNullOrWhiteSpace(targetHost))
            options.Pinner.VerifyPins(targetHost, verifiedChain);

        return verifiedChain;
    }

    private static bool TryBuildChain(
        List<DerCertificate> currentChain,
        List<DerCertificate> intermediates,
        string? targetHost,
        CertificateVerifyOptions options,
        DateTimeOffset now,
        ref int signatureChecks,
        ref string? lastFailure)
    {
        var child = currentChain[^1];

        if (currentChain.Count >= options.MaxChainLength)
        {
            lastFailure ??= $"x509: no chain of at most {options.MaxChainLength} certificates reaches a trusted root";
            return false;
        }

        var candidates = CollectCandidateIssuers(child, currentChain, intermediates, options);
        if (candidates.Count == 0)
        {
            lastFailure ??= $"x509: certificate signed by unknown authority ('{child.SubjectText}')";
            return false;
        }

        for (var i = 0; i < candidates.Count; i++)
        {
            var (issuer, isRoot) = candidates[i];
            var edgeError = ValidateChainEdge(child, issuer, isRoot, currentChain, targetHost, options, now, ref signatureChecks);
            if (edgeError is not null)
            {
                lastFailure = edgeError;
                continue;
            }

            currentChain.Add(issuer);
            if (isRoot)
                return true;

            if (TryBuildChain(currentChain, intermediates, targetHost, options, now, ref signatureChecks, ref lastFailure))
                return true;

            currentChain.RemoveAt(currentChain.Count - 1);
        }

        return false;
    }

    private static List<(DerCertificate Cert, bool IsRoot)> CollectCandidateIssuers(
        DerCertificate child,
        List<DerCertificate> currentChain,
        List<DerCertificate> intermediates,
        CertificateVerifyOptions options)
    {
        var result = new List<(DerCertificate Cert, bool IsRoot)>();
        var seenInList = new HashSet<ReadOnlyMemory<byte>>(ReadOnlyMemoryByteComparer.Instance);
        for (var i = 0; i < currentChain.Count; i++)
            seenInList.Add(currentChain[i].RawDer);

        var matchingRoots = new List<DerCertificate>();
        if (options.CustomRoots is not null)
        {
            var found = options.CustomRoots.FindBySubjectRaw(child.IssuerRaw);
            for (var i = 0; i < found.Count; i++)
            {
                if (seenInList.Add(found[i].RawDer))
                    matchingRoots.Add(found[i]);
            }
        }

        if (options.UseEmbeddedDefaultRoots)
        {
            var found = RootCertificateDatabase.Default.FindBySubjectRaw(child.IssuerRaw);
            for (var i = 0; i < found.Count; i++)
            {
                if (seenInList.Add(found[i].RawDer))
                    matchingRoots.Add(found[i]);
            }
        }

        PrioritizeKeyIdMatch(matchingRoots, child.AuthorityKeyId);
        for (var i = 0; i < matchingRoots.Count; i++)
            result.Add((matchingRoots[i], true));

        var matchingMids = new List<DerCertificate>();
        for (var i = 0; i < intermediates.Count; i++)
        {
            var mid = intermediates[i];
            if (mid.SubjectRaw.Span.SequenceEqual(child.IssuerRaw.Span) && seenInList.Add(mid.RawDer))
                matchingMids.Add(mid);
        }

        PrioritizeKeyIdMatch(matchingMids, child.AuthorityKeyId);
        for (var i = 0; i < matchingMids.Count; i++)
            result.Add((matchingMids[i], false));

        return result;
    }

    private static void PrioritizeKeyIdMatch(List<DerCertificate> candidates, byte[]? authorityKeyId)
    {
        if (candidates.Count <= 1 || authorityKeyId is null || authorityKeyId.Length == 0)
            return;

        var insertIndex = 0;
        for (var i = 0; i < candidates.Count; i++)
        {
            var ski = candidates[i].SubjectKeyId;
            if (ski is not null && ski.AsSpan().SequenceEqual(authorityKeyId))
            {
                if (i != insertIndex)
                    (candidates[insertIndex], candidates[i]) = (candidates[i], candidates[insertIndex]);
                insertIndex++;
            }
        }
    }

    private static string? ValidateChainEdge(
        DerCertificate child,
        DerCertificate issuer,
        bool isRoot,
        List<DerCertificate> currentChain,
        string? targetHost,
        CertificateVerifyOptions options,
        DateTimeOffset now,
        ref int signatureChecks)
    {
        if (issuer.UnhandledCriticalExtensions.Count > 0)
            return $"x509: certificate '{issuer.SubjectText}' contains unhandled critical extension(s) ({string.Join(", ", issuer.UnhandledCriticalExtensions)})";

        if (!options.AllowSha1 && child.UsesSha1Signature)
            return $"x509: certificate '{child.SubjectText}' is signed with insecure algorithm SHA-1";

        if (now < issuer.NotBefore)
            return $"x509: certificate '{issuer.SubjectText}' is not yet valid: current time {now:O} before {issuer.NotBefore:O}";

        if (now > issuer.NotAfter)
            return $"x509: certificate '{issuer.SubjectText}' has expired: current time {now:O} after {issuer.NotAfter:O}";

        if (!issuer.HasBasicConstraints || !issuer.IsCa)
            return $"x509: certificate '{issuer.SubjectText}' is not authorized to sign other certificates (not a CA)";

        if (issuer.HasKeyUsage && (issuer.KeyUsage & X509KeyUsageFlagsLite.KeyCertSign) == 0)
            return $"x509: certificate '{issuer.SubjectText}' is not authorized to sign certificates (keyUsage lacks keyCertSign)";

        if (!isRoot && !HasCompatibleServerAuthEku(issuer))
            return $"x509: certificate '{issuer.SubjectText}' specifies an incompatible key usage (no serverAuth)";

        if (issuer.PathLenConstraint.HasValue)
        {
            var intermediateCount = 0;
            // currentChain[0] is the end-entity leaf; currentChain[1..] are intermediate CAs below issuer.
            // Per RFC 5280 §6.1.4(l), self-issued intermediate CAs do not consume pathLenConstraint.
            for (var i = 1; i < currentChain.Count; i++)
            {
                if (!currentChain[i].IsSelfSigned)
                    intermediateCount++;
            }

            if (intermediateCount > issuer.PathLenConstraint.Value)
                return $"x509: too many intermediates for path length constraint of '{issuer.SubjectText}' ({intermediateCount} > {issuer.PathLenConstraint.Value})";
        }

        if (issuer.NameConstraints is not null)
        {
            var ncError = CheckNameConstraints(issuer.NameConstraints, currentChain, targetHost);
            if (ncError is not null)
                return ncError;
        }

        signatureChecks++;
        if (signatureChecks > options.MaxSignatureChecks)
            throw new CertificateValidationException("x509: signature check attempts limit reached while verifying certificate chain");

        if (!child.VerifySignature(issuer))
            return $"x509: certificate '{child.SubjectText}' has an invalid signature from '{issuer.SubjectText}'";

        return null;
    }

    private static string? CheckNameConstraints(NameConstraintsExt nc, List<DerCertificate> descendants, string? targetHost)
    {
        for (var i = 0; i < descendants.Count; i++)
        {
            var cert = descendants[i];

            if (cert.HasSubjectAltName)
            {
                for (var d = 0; d < cert.SanDnsNames.Count; d++)
                {
                    var dns = cert.SanDnsNames[d];
                    var err = CheckDnsAgainstNameConstraints(dns, nc);
                    if (err is not null)
                        return err;
                }

                for (var p = 0; p < cert.SanIpAddresses.Count; p++)
                {
                    var ip = cert.SanIpAddresses[p];
                    var err = CheckIpAgainstNameConstraints(ip, nc);
                    if (err is not null)
                        return err;
                }
            }
            else if (i == 0 &&
                     !string.IsNullOrEmpty(cert.SubjectCommonName) &&
                     (nc.PermittedDns.Count > 0 || nc.ExcludedDns.Count > 0) &&
                     (cert.SubjectCommonName.Contains('.') || !string.IsNullOrEmpty(targetHost)) &&
                     IsValidHostnamePattern(cert.SubjectCommonName, allowWildcard: true))
            {
                var err = CheckDnsAgainstNameConstraints(cert.SubjectCommonName, nc);
                if (err is not null)
                    return err;
            }
        }

        return null;
    }

    private static string? CheckDnsAgainstNameConstraints(string dnsName, NameConstraintsExt nc)
    {
        for (var i = 0; i < nc.ExcludedDns.Count; i++)
        {
            var excluded = nc.ExcludedDns[i];
            if (MatchDnsConstraint(dnsName, excluded) ||
                (dnsName.StartsWith("*.", StringComparison.Ordinal) && MatchDnsName(dnsName, excluded)))
            {
                return $"x509: a root or intermediate certificate is not authorized to sign for domain '{dnsName}' (excluded by '{excluded}')";
            }
        }

        if (nc.PermittedDns.Count > 0)
        {
            var matched = false;
            for (var i = 0; i < nc.PermittedDns.Count; i++)
            {
                if (MatchDnsConstraint(dnsName, nc.PermittedDns[i]))
                {
                    matched = true;
                    break;
                }
            }

            if (!matched)
                return $"x509: a root or intermediate certificate is not authorized to sign for domain '{dnsName}'";
        }

        return null;
    }

    private static string? CheckIpAgainstNameConstraints(IPAddress ip, NameConstraintsExt nc)
    {
        var ipBytes = ip.GetAddressBytes();

        for (var i = 0; i < nc.ExcludedIpSubnets.Count; i++)
        {
            if (MatchIpSubnet(ipBytes, nc.ExcludedIpSubnets[i]))
                return $"x509: a root or intermediate certificate is not authorized to sign for IP '{ip}' (excluded subnet)";
        }

        if (nc.PermittedIpSubnets.Count > 0)
        {
            var matched = false;
            for (var i = 0; i < nc.PermittedIpSubnets.Count; i++)
            {
                if (MatchIpSubnet(ipBytes, nc.PermittedIpSubnets[i]))
                {
                    matched = true;
                    break;
                }
            }

            if (!matched)
                return $"x509: a root or intermediate certificate is not authorized to sign for IP '{ip}'";
        }

        return null;
    }

    private static bool MatchIpSubnet(ReadOnlySpan<byte> ipBytes, (byte[] Net, byte[] Mask) subnet)
    {
        if (ipBytes.Length != subnet.Net.Length || subnet.Net.Length != subnet.Mask.Length)
            return false;

        for (var i = 0; i < ipBytes.Length; i++)
        {
            if ((ipBytes[i] & subnet.Mask[i]) != (subnet.Net[i] & subnet.Mask[i]))
                return false;
        }
        return true;
    }

    /// <summary>
    /// RFC 5280 §4.2.1.10 dNSName constraint matching:
    /// Leading dot (e.g. <c>.corp.example</c>) requires a strict subdomain (<c>a.corp.example</c>, not <c>corp.example</c>).
    /// Without a leading dot (e.g. <c>corp.example</c>), matches the domain itself or any subdomain.
    /// </summary>
    private static bool MatchDnsConstraint(string name, string constraint)
    {
        if (constraint.Length == 0)
            return true;

        var normalizedName = name.EndsWith('.') ? name[..^1] : name;
        if (normalizedName.Length == 0 || normalizedName.StartsWith('.'))
            return false;

        var requireSubdomain = constraint[0] == '.';
        var constraintCore = requireSubdomain ? constraint[1..] : constraint;
        if (constraintCore.EndsWith('.'))
            constraintCore = constraintCore[..^1];

        var nameLabels = normalizedName.Split('.');
        for (var i = 0; i < nameLabels.Length; i++)
        {
            if (nameLabels[i].Length == 0)
                return false;
        }

        if (constraintCore.Length == 0)
            return requireSubdomain;

        var constraintLabels = constraintCore.Split('.');
        for (var i = 0; i < constraintLabels.Length; i++)
        {
            if (constraintLabels[i].Length == 0)
                return false;
        }

        if (nameLabels.Length < constraintLabels.Length)
            return false;

        if (requireSubdomain && nameLabels.Length == constraintLabels.Length)
            return false;

        var offset = nameLabels.Length - constraintLabels.Length;
        for (var i = 0; i < constraintLabels.Length; i++)
        {
            if (!string.Equals(nameLabels[offset + i], constraintLabels[i], StringComparison.OrdinalIgnoreCase))
                return false;
        }

        return true;
    }

    private static bool IsTrustedRoot(DerCertificate cert, CertificateVerifyOptions options) =>
        (options.CustomRoots is not null && options.CustomRoots.Contains(cert)) ||
        (options.UseEmbeddedDefaultRoots && RootCertificateDatabase.Default.Contains(cert));

    private static void ValidateValidityWindow(DerCertificate cert, DateTimeOffset now)
    {
        if (now < cert.NotBefore)
            throw new CertificateValidationException($"x509: certificate '{cert.SubjectText}' is not yet valid: current time {now:O} is before {cert.NotBefore:O}");
        if (now > cert.NotAfter)
            throw new CertificateValidationException($"x509: certificate '{cert.SubjectText}' has expired: current time {now:O} is after {cert.NotAfter:O}");
    }

    private static bool HasCompatibleServerAuthEku(DerCertificate cert)
    {
        if (cert.ExtendedKeyUsages.Count == 0)
            return true;

        for (var i = 0; i < cert.ExtendedKeyUsages.Count; i++)
        {
            switch (cert.ExtendedKeyUsages[i])
            {
                case EkuServerAuth:
                case EkuAny:
                case EkuNetscapeSgc:
                case EkuMicrosoftSgc:
                    return true;
            }
        }
        return false;
    }

    private static void VerifyHostname(DerCertificate leaf, string targetHost)
    {
        if (TryParseStrictIpAddress(targetHost, out var targetIp) && targetIp is not null)
        {
            if (leaf.SanIpAddresses.Count == 0)
            {
                throw new CertificateValidationException(
                    $"x509: cannot validate certificate for {targetHost} because it doesn't contain any IP SANs");
            }

            var targetBytes = targetIp.GetAddressBytes();
            for (var i = 0; i < leaf.SanIpAddresses.Count; i++)
            {
                if (leaf.SanIpAddresses[i].GetAddressBytes().AsSpan().SequenceEqual(targetBytes))
                    return;
            }

            throw new CertificateValidationException(
                $"x509: certificate is valid for [{string.Join(", ", leaf.SanIpAddresses)}], not {targetHost}");
        }

        var normalizedHost = targetHost.EndsWith('.') ? targetHost[..^1] : targetHost;
        if (!IsValidHostnamePattern(normalizedHost, allowWildcard: false))
            throw new CertificateValidationException($"x509: invalid target hostname '{targetHost}'");

        if (leaf.HasSubjectAltName)
        {
            for (var i = 0; i < leaf.SanDnsNames.Count; i++)
            {
                if (MatchDnsName(leaf.SanDnsNames[i], normalizedHost))
                    return;
            }

            if (leaf.SanDnsNames.Count == 0)
            {
                throw new CertificateValidationException(
                    $"x509: certificate is not valid for any names, but wanted to match {targetHost}");
            }

            throw new CertificateValidationException(
                $"x509: certificate is valid for [{string.Join(", ", leaf.SanDnsNames)}], not {targetHost}");
        }

        // RFC 6125 CN fallback ONLY when zero SAN entries are present
        if (!string.IsNullOrEmpty(leaf.SubjectCommonName) && MatchDnsName(leaf.SubjectCommonName, normalizedHost))
            return;

        throw new CertificateValidationException(
            $"x509: certificate relies on Common Name '{leaf.SubjectCommonName}' which does not match '{targetHost}'");
    }

    private static bool TryParseStrictIpAddress(string host, out IPAddress? ip)
    {
        var trimmed = host;
        if (trimmed.Length >= 2 && trimmed[0] == '[' && trimmed[^1] == ']')
            trimmed = trimmed[1..^1];

        var hostType = Uri.CheckHostName(trimmed);
        if (hostType is not (UriHostNameType.IPv4 or UriHostNameType.IPv6))
        {
            ip = null;
            return false;
        }

        return IPAddress.TryParse(trimmed, out ip);
    }

    private static bool IsValidHostnamePattern(string name, bool allowWildcard)
    {
        if (string.IsNullOrEmpty(name) || name == "*")
            return false;

        var labels = name.Split('.');
        for (var i = 0; i < labels.Length; i++)
        {
            var label = labels[i];
            if (label.Length == 0)
                return false;

            if (allowWildcard && i == 0 && label == "*")
                continue;

            for (var j = 0; j < label.Length; j++)
            {
                var c = label[j];
                var ok = (c is >= 'a' and <= 'z') ||
                         (c is >= 'A' and <= 'Z') ||
                         (c is >= '0' and <= '9') ||
                         c == '_' ||
                         (c == '-' && j > 0);
                if (!ok)
                    return false;
            }
        }
        return true;
    }

    /// <summary>
    /// RFC 6125 DNS matching: exact case-insensitive match or single left-most label wildcard
    /// (<c>*.foo.bar</c> matches <c>a.foo.bar</c>, rejects <c>a.b.foo.bar</c> and <c>foo.bar</c>).
    /// </summary>
    private static bool MatchDnsName(string pattern, string host)
    {
        if (!IsValidHostnamePattern(pattern, allowWildcard: true))
            return false;

        var pLabels = pattern.Split('.');
        var hLabels = host.Split('.');
        if (pLabels.Length != hLabels.Length)
            return false;

        for (var i = 0; i < pLabels.Length; i++)
        {
            if (i == 0 && pLabels[0] == "*")
            {
                if (pLabels.Length < 2)
                    return false;
                continue;
            }

            if (!string.Equals(pLabels[i], hLabels[i], StringComparison.OrdinalIgnoreCase))
                return false;
        }

        return true;
    }
}
