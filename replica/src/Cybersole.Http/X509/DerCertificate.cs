using System.Net;
using System.Text;
using Cybersole.Http.Crypto;

namespace Cybersole.Http.X509;

/// <summary>
/// RFC 5280 KeyUsage extension bit flags (OID 2.5.29.15).
/// Bit positions match big-endian ASN.1 BIT STRING indices 0..8.
/// </summary>
[Flags]
public enum X509KeyUsageFlagsLite
{
    None = 0,
    DigitalSignature = 1 << 0,
    NonRepudiation = 1 << 1,
    KeyEncipherment = 1 << 2,
    DataEncipherment = 1 << 3,
    KeyAgreement = 1 << 4,
    KeyCertSign = 1 << 5,
    CrlSign = 1 << 6,
    EncipherOnly = 1 << 7,
    DecipherOnly = 1 << 8,
}

/// <summary>
/// Parsed RFC 5280 Name Constraints extension (OID 2.5.29.30).
/// </summary>
public sealed class NameConstraintsExt
{
    public IReadOnlyList<string> PermittedDns { get; init; } = Array.Empty<string>();
    public IReadOnlyList<string> ExcludedDns { get; init; } = Array.Empty<string>();
    public IReadOnlyList<(byte[] Net, byte[] Mask)> PermittedIpSubnets { get; init; } = Array.Empty<(byte[] Net, byte[] Mask)>();
    public IReadOnlyList<(byte[] Net, byte[] Mask)> ExcludedIpSubnets { get; init; } = Array.Empty<(byte[] Net, byte[] Mask)>();
}

/// <summary>
/// Pure managed ASN.1 DER X.509 certificate representation (RFC 5280).
/// </summary>
public sealed class DerCertificate
{
    private static readonly HashSet<string> UnderstoodCriticalExtensionOids = new(StringComparer.Ordinal)
    {
        "2.5.29.14",         // SubjectKeyIdentifier
        "2.5.29.15",         // KeyUsage
        "2.5.29.17",         // SubjectAltName
        "2.5.29.19",         // BasicConstraints
        "2.5.29.30",         // NameConstraints
        "2.5.29.31",         // CRLDistributionPoints
        "2.5.29.32",         // CertificatePolicies
        "2.5.29.33",         // PolicyMappings
        "2.5.29.35",         // AuthorityKeyIdentifier
        "2.5.29.36",         // PolicyConstraints
        "2.5.29.37",         // ExtKeyUsage
        "2.5.29.54",         // InhibitAnyPolicy
        "1.3.6.1.5.5.7.1.1", // AuthorityInfoAccess
    };

    private DerCertificate(
        ReadOnlyMemory<byte> rawDer,
        ReadOnlyMemory<byte> tbsCertificateRaw,
        string signatureAlgorithmOid,
        ReadOnlyMemory<byte> signatureAlgorithmParametersRaw,
        byte[] signatureValueBytes,
        int version,
        byte[] serialNumber,
        ReadOnlyMemory<byte> issuerRaw,
        ReadOnlyMemory<byte> subjectRaw,
        string? subjectCommonName,
        string subjectText,
        IReadOnlyList<(string Oid, string Value)> subjectRdns,
        IReadOnlyList<(string Oid, string Value)> issuerRdns,
        DateTimeOffset notBefore,
        DateTimeOffset notAfter,
        ReadOnlyMemory<byte> subjectPublicKeyInfoRaw,
        byte[] spkiSha256,
        string publicKeyAlgorithmOid,
        string? publicKeyCurveOid,
        byte[] publicKeyBitString,
        bool hasBasicConstraints,
        bool isCa,
        int? pathLenConstraint,
        bool hasKeyUsage,
        X509KeyUsageFlagsLite keyUsage,
        IReadOnlyList<string> extendedKeyUsages,
        bool hasSubjectAltName,
        IReadOnlyList<string> sanDnsNames,
        IReadOnlyList<IPAddress> sanIpAddresses,
        NameConstraintsExt? nameConstraints,
        byte[]? subjectKeyId,
        byte[]? authorityKeyId,
        IReadOnlyList<string> unhandledCriticalExtensions)
    {
        RawDer = rawDer;
        TbsCertificateRaw = tbsCertificateRaw;
        SignatureAlgorithmOid = signatureAlgorithmOid;
        SignatureAlgorithmParametersRaw = signatureAlgorithmParametersRaw;
        SignatureValueBytes = signatureValueBytes;
        Version = version;
        SerialNumber = serialNumber;
        IssuerRaw = issuerRaw;
        SubjectRaw = subjectRaw;
        SubjectCommonName = subjectCommonName;
        SubjectText = subjectText;
        SubjectRdns = subjectRdns;
        IssuerRdns = issuerRdns;
        NotBefore = notBefore;
        NotAfter = notAfter;
        SubjectPublicKeyInfoRaw = subjectPublicKeyInfoRaw;
        SpkiSha256 = spkiSha256;
        PinSha256Base64 = Convert.ToBase64String(spkiSha256);
        PinSha256 = "pin-sha256=" + PinSha256Base64;
        PublicKeyAlgorithmOid = publicKeyAlgorithmOid;
        PublicKeyCurveOid = publicKeyCurveOid;
        PublicKeyBitString = publicKeyBitString;
        HasBasicConstraints = hasBasicConstraints;
        IsCa = isCa;
        PathLenConstraint = pathLenConstraint;
        HasKeyUsage = hasKeyUsage;
        KeyUsage = keyUsage;
        ExtendedKeyUsages = extendedKeyUsages;
        HasSubjectAltName = hasSubjectAltName;
        SanDnsNames = sanDnsNames;
        SanIpAddresses = sanIpAddresses;
        NameConstraints = nameConstraints;
        SubjectKeyId = subjectKeyId;
        AuthorityKeyId = authorityKeyId;
        UnhandledCriticalExtensions = unhandledCriticalExtensions;
    }

    public ReadOnlyMemory<byte> RawDer { get; }
    public ReadOnlyMemory<byte> TbsCertificateRaw { get; }
    public string SignatureAlgorithmOid { get; }
    public ReadOnlyMemory<byte> SignatureAlgorithmParametersRaw { get; }
    public byte[] SignatureValueBytes { get; }
    public int Version { get; }
    public byte[] SerialNumber { get; }
    public ReadOnlyMemory<byte> IssuerRaw { get; }
    public ReadOnlyMemory<byte> SubjectRaw { get; }
    public string? SubjectCommonName { get; }
    public string SubjectText { get; }
    public IReadOnlyList<(string Oid, string Value)> SubjectRdns { get; }
    public IReadOnlyList<(string Oid, string Value)> IssuerRdns { get; }
    public DateTimeOffset NotBefore { get; }
    public DateTimeOffset NotAfter { get; }
    public ReadOnlyMemory<byte> SubjectPublicKeyInfoRaw { get; }
    public byte[] SpkiSha256 { get; }
    public string PinSha256Base64 { get; }
    public string PinSha256 { get; }
    public string PublicKeyAlgorithmOid { get; }
    public string? PublicKeyCurveOid { get; }
    public byte[] PublicKeyBitString { get; }
    public bool HasBasicConstraints { get; }
    public bool IsCa { get; }
    public int? PathLenConstraint { get; }
    public bool HasKeyUsage { get; }
    public X509KeyUsageFlagsLite KeyUsage { get; }
    public IReadOnlyList<string> ExtendedKeyUsages { get; }
    public bool HasSubjectAltName { get; }
    public IReadOnlyList<string> SanDnsNames { get; }
    public IReadOnlyList<IPAddress> SanIpAddresses { get; }
    public NameConstraintsExt? NameConstraints { get; }
    public byte[]? SubjectKeyId { get; }
    public byte[]? AuthorityKeyId { get; }
    public IReadOnlyList<string> UnhandledCriticalExtensions { get; }

    public bool IsSelfSigned => SubjectRaw.Span.SequenceEqual(IssuerRaw.Span);

    internal bool UsesSha1Signature
    {
        get
        {
            if (SignatureAlgorithmOid is "1.2.840.113549.1.1.5" or "1.3.14.3.2.29" or "1.2.840.10045.4.1")
                return true;

            if (SignatureAlgorithmOid == "1.2.840.113549.1.1.10" &&
                TryParsePssParameters(SignatureAlgorithmParametersRaw, out var hashAlg, out _))
            {
                return hashAlg == HashAlgorithmKind.Sha1;
            }

            return false;
        }
    }

    public static bool TryParse(ReadOnlySpan<byte> der, out DerCertificate? certificate)
    {
        try
        {
            certificate = Parse(der);
            return true;
        }
        catch (FormatException)
        {
            certificate = null;
            return false;
        }
    }

    public static DerCertificate Parse(ReadOnlySpan<byte> der)
    {
        if (der.IsEmpty)
            throw new FormatException("Certificate DER buffer cannot be empty.");

        var raw = der.ToArray();
        var rootNode = Asn1Reader.ReadSingle(raw);
        if (!rootNode.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
            throw new FormatException("X.509 certificate root must be an ASN.1 SEQUENCE.");

        var certCursor = new Asn1Cursor(rootNode.Content);
        var tbsNode = certCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var outerSigAlgNode = certCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var sigBitNode = certCursor.ReadUniversal(Asn1Tag.TagBitString, false);
        certCursor.ExpectEnd();

        var (outerSigOid, outerSigParamsRaw) = ParseAlgorithmIdentifier(outerSigAlgNode);
        var sigBytes = Asn1Reader.ReadBitString(sigBitNode.ContentSpan, out var sigUnusedBits);
        if (sigUnusedBits != 0)
            throw new FormatException("X.509 signatureValue BIT STRING must have 0 unused bits.");

        var tbsCursor = new Asn1Cursor(tbsNode.Content);

        // Optional [0] EXPLICIT Version DEFAULT v1(0)
        var version = 0;
        if (tbsCursor.TryReadContextSpecific(0, true, out var versionWrapper))
        {
            var verCursor = new Asn1Cursor(versionWrapper.Content);
            var verIntNode = verCursor.ReadUniversal(Asn1Tag.TagInteger, false);
            verCursor.ExpectEnd();
            version = Asn1Reader.ReadSmallInt(verIntNode.ContentSpan);
            if (version is < 0 or > 2)
                throw new FormatException($"Unsupported X.509 certificate version: {version}.");
        }

        var serialNode = tbsCursor.ReadUniversal(Asn1Tag.TagInteger, false);
        var serialNumber = Asn1Reader.ReadIntegerBytes(serialNode.ContentSpan);

        var innerSigAlgNode = tbsCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var (innerSigOid, _) = ParseAlgorithmIdentifier(innerSigAlgNode);
        if (!string.Equals(outerSigOid, innerSigOid, StringComparison.Ordinal))
            throw new FormatException($"X.509 TBSCertificate signature OID '{innerSigOid}' does not match outer signatureAlgorithm '{outerSigOid}'.");

        var issuerNode = tbsCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var issuerRdns = ParseName(issuerNode);

        var validityNode = tbsCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var validityCursor = new Asn1Cursor(validityNode.Content);
        var notBefore = Asn1Reader.ParseTime(validityCursor.ReadNext());
        var notAfter = Asn1Reader.ParseTime(validityCursor.ReadNext());
        validityCursor.ExpectEnd();

        var subjectNode = tbsCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var subjectRdns = ParseName(subjectNode);
        string? subjectCn = null;
        for (var i = 0; i < subjectRdns.Count; i++)
        {
            if (subjectRdns[i].Oid == "2.5.4.3")
                subjectCn = subjectRdns[i].Value;
        }
        var subjectText = FormatRdns(subjectRdns);

        var spkiNode = tbsCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var spkiRaw = spkiNode.HeaderAndContent;
        var spkiSha256 = HashPrimitives.Sha256(spkiRaw.Span);

        var spkiCursor = new Asn1Cursor(spkiNode.Content);
        var spkiAlgNode = spkiCursor.ReadUniversal(Asn1Tag.TagSequence, true);
        var (pubAlgOid, pubAlgParamsRaw) = ParseAlgorithmIdentifier(spkiAlgNode);
        string? pubCurveOid = null;
        if (pubAlgOid == "1.2.840.10045.2.1") // id-ecPublicKey
        {
            if (pubAlgParamsRaw.IsEmpty)
                throw new FormatException("ECDSA SubjectPublicKeyInfo is missing namedCurve OID parameter.");
            var curveNode = Asn1Reader.ReadSingle(pubAlgParamsRaw);
            if (!curveNode.Tag.IsUniversal(Asn1Tag.TagObjectIdentifier) || curveNode.IsConstructed)
                throw new FormatException("ECDSA SubjectPublicKeyInfo parameter must be a namedCurve OID.");
            pubCurveOid = Asn1Reader.ReadOid(curveNode.ContentSpan);
        }

        var spkiKeyBitNode = spkiCursor.ReadUniversal(Asn1Tag.TagBitString, false);
        spkiCursor.ExpectEnd();
        var pubKeyBits = Asn1Reader.ReadBitString(spkiKeyBitNode.ContentSpan, out var pkUnusedBits);
        if (pkUnusedBits != 0)
            throw new FormatException("SubjectPublicKey BIT STRING must have 0 unused bits.");

        // Optional issuerUniqueID [1] IMPLICIT (v2+)
        if (tbsCursor.TryReadContextSpecific(1, out _))
        {
            if (version < 1)
                throw new FormatException("issuerUniqueID is only permitted in X.509 v2 or v3 certificates.");
        }

        // Optional subjectUniqueID [2] IMPLICIT (v2+)
        if (tbsCursor.TryReadContextSpecific(2, out _))
        {
            if (version < 1)
                throw new FormatException("subjectUniqueID is only permitted in X.509 v2 or v3 certificates.");
        }

        var hasBasicConstraints = false;
        var isCa = false;
        int? pathLenConstraint = null;
        var hasKeyUsage = false;
        var keyUsage = X509KeyUsageFlagsLite.None;
        var ekus = new List<string>();
        var hasSan = false;
        var sanDnsNames = new List<string>();
        var sanIpAddresses = new List<IPAddress>();
        NameConstraintsExt? nameConstraints = null;
        byte[]? subjectKeyId = null;
        byte[]? authorityKeyId = null;
        var unhandledCritical = new List<string>();

        // Optional extensions [3] EXPLICIT (v3)
        if (tbsCursor.TryReadContextSpecific(3, true, out var extsWrapper))
        {
            if (version != 2)
                throw new FormatException("extensions field is only permitted in X.509 v3 certificates.");

            var extsWrapperCursor = new Asn1Cursor(extsWrapper.Content);
            var extsSeq = extsWrapperCursor.ReadUniversal(Asn1Tag.TagSequence, true);
            extsWrapperCursor.ExpectEnd();

            var seenOids = new HashSet<string>(StringComparer.Ordinal);
            var extListCursor = new Asn1Cursor(extsSeq.Content);
            while (extListCursor.HasRemaining)
            {
                var extNode = extListCursor.ReadUniversal(Asn1Tag.TagSequence, true);
                var extCursor = new Asn1Cursor(extNode.Content);

                var oidNode = extCursor.ReadUniversal(Asn1Tag.TagObjectIdentifier, false);
                var extOid = Asn1Reader.ReadOid(oidNode.ContentSpan);
                if (!seenOids.Add(extOid))
                    throw new FormatException($"Duplicate X.509 extension OID: {extOid}.");

                var critical = false;
                if (extCursor.TryPeekTag(out var nextTag) && nextTag.IsUniversal(Asn1Tag.TagBoolean))
                {
                    var boolNode = extCursor.ReadUniversal(Asn1Tag.TagBoolean, false);
                    critical = Asn1Reader.ReadBoolean(boolNode.ContentSpan);
                }

                var valNode = extCursor.ReadUniversal(Asn1Tag.TagOctetString, false);
                extCursor.ExpectEnd();

                var extHandled = true;
                switch (extOid)
                {
                    case "2.5.29.14": // SubjectKeyIdentifier
                        subjectKeyId = ParseOctetStringExtension(valNode.Content);
                        break;
                    case "2.5.29.15": // KeyUsage
                        keyUsage = ParseKeyUsage(valNode.Content);
                        hasKeyUsage = true;
                        break;
                    case "2.5.29.17": // SubjectAltName
                        hasSan = true;
                        ParseSan(valNode.Content, sanDnsNames, sanIpAddresses);
                        break;
                    case "2.5.29.19": // BasicConstraints
                        (isCa, pathLenConstraint) = ParseBasicConstraints(valNode.Content);
                        hasBasicConstraints = true;
                        break;
                    case "2.5.29.30": // NameConstraints
                        nameConstraints = ParseNameConstraints(valNode.Content, out var ncFullyUnderstood);
                        extHandled = ncFullyUnderstood;
                        break;
                    case "2.5.29.35": // AuthorityKeyIdentifier
                        authorityKeyId = ParseAuthorityKeyId(valNode.Content);
                        break;
                    case "2.5.29.37": // ExtendedKeyUsage
                        ParseExtendedKeyUsage(valNode.Content, ekus);
                        break;
                    default:
                        extHandled = UnderstoodCriticalExtensionOids.Contains(extOid);
                        break;
                }

                if (critical && !extHandled)
                    unhandledCritical.Add(extOid);
            }
            extListCursor.ExpectEnd();
        }

        tbsCursor.ExpectEnd();

        return new DerCertificate(
            raw,
            tbsNode.HeaderAndContent,
            outerSigOid,
            outerSigParamsRaw,
            sigBytes.ToArray(),
            version,
            serialNumber,
            issuerNode.HeaderAndContent,
            subjectNode.HeaderAndContent,
            subjectCn,
            subjectText,
            subjectRdns,
            issuerRdns,
            notBefore,
            notAfter,
            spkiRaw,
            spkiSha256,
            pubAlgOid,
            pubCurveOid,
            pubKeyBits.ToArray(),
            hasBasicConstraints,
            isCa,
            pathLenConstraint,
            hasKeyUsage,
            keyUsage,
            ekus,
            hasSan,
            sanDnsNames,
            sanIpAddresses,
            nameConstraints,
            subjectKeyId,
            authorityKeyId,
            unhandledCritical);
    }

    /// <summary>
    /// Verifies this certificate's signature against <paramref name="issuer"/>'s public key
    /// using pure managed cryptography (<see cref="Cybersole.Http.Crypto"/>).
    /// </summary>
    public bool VerifySignature(DerCertificate issuer)
    {
        ArgumentNullException.ThrowIfNull(issuer);

        try
        {
            return VerifySignatureCore(issuer);
        }
        catch (FormatException)
        {
            return false;
        }
    }

    private bool VerifySignatureCore(DerCertificate issuer)
    {
        var tbs = TbsCertificateRaw.Span;
        var sig = SignatureValueBytes;

        switch (SignatureAlgorithmOid)
        {
            // RSA PKCS#1 v1.5
            case "1.2.840.113549.1.1.5":  // sha1WithRSAEncryption
            case "1.3.14.3.2.29":        // sha1WithRSASignature
                return VerifyRsaPkcs1(issuer, HashAlgorithmKind.Sha1, tbs, sig);
            case "1.2.840.113549.1.1.11": // sha256WithRSAEncryption
                return VerifyRsaPkcs1(issuer, HashAlgorithmKind.Sha256, tbs, sig);
            case "1.2.840.113549.1.1.12": // sha384WithRSAEncryption
                return VerifyRsaPkcs1(issuer, HashAlgorithmKind.Sha384, tbs, sig);
            case "1.2.840.113549.1.1.13": // sha512WithRSAEncryption
                return VerifyRsaPkcs1(issuer, HashAlgorithmKind.Sha512, tbs, sig);

            // RSA-PSS
            case "1.2.840.113549.1.1.10":
                return VerifyRsaPss(issuer, tbs, sig);

            // ECDSA
            case "1.2.840.10045.4.1":     // ecdsa-with-SHA1
                return VerifyEcdsa(issuer, HashAlgorithmKind.Sha1, tbs, sig);
            case "1.2.840.10045.4.3.2":   // ecdsa-with-SHA256
                return VerifyEcdsa(issuer, HashAlgorithmKind.Sha256, tbs, sig);
            case "1.2.840.10045.4.3.3":   // ecdsa-with-SHA384
                return VerifyEcdsa(issuer, HashAlgorithmKind.Sha384, tbs, sig);
            case "1.2.840.10045.4.3.4":   // ecdsa-with-SHA512
                return VerifyEcdsa(issuer, HashAlgorithmKind.Sha512, tbs, sig);

            // Ed25519
            case "1.3.101.112":
                return VerifyEd25519(issuer, tbs, sig);

            default:
                return false;
        }
    }

    private bool VerifyRsaPkcs1(DerCertificate issuer, HashAlgorithmKind hashAlg, ReadOnlySpan<byte> tbs, ReadOnlySpan<byte> sig)
    {
        if (!IsAbsentOrDerNull(SignatureAlgorithmParametersRaw.Span))
            return false;
        if (issuer.PublicKeyAlgorithmOid != "1.2.840.113549.1.1.1")
            return false;
        if (!RsaPrimitives.TryParseRsaPublicKeyDer(issuer.PublicKeyBitString, out var modulus, out var exponent))
            return false;
        return RsaPrimitives.VerifyPkcs1(modulus, exponent, hashAlg, tbs, sig);
    }

    private bool VerifyRsaPss(DerCertificate issuer, ReadOnlySpan<byte> tbs, ReadOnlySpan<byte> sig)
    {
        if (issuer.PublicKeyAlgorithmOid is not ("1.2.840.113549.1.1.1" or "1.2.840.113549.1.1.10"))
            return false;
        if (!TryParsePssParameters(SignatureAlgorithmParametersRaw, out var hashAlg, out var saltLength))
            return false;
        if (!RsaPrimitives.TryParseRsaPublicKeyDer(issuer.PublicKeyBitString, out var modulus, out var exponent))
            return false;
        return RsaPrimitives.VerifyPss(modulus, exponent, hashAlg, tbs, sig, saltLength);
    }

    private bool VerifyEcdsa(DerCertificate issuer, HashAlgorithmKind hashAlg, ReadOnlySpan<byte> tbs, ReadOnlySpan<byte> sig)
    {
        if (!SignatureAlgorithmParametersRaw.IsEmpty)
            return false;
        if (issuer.PublicKeyAlgorithmOid != "1.2.840.10045.2.1" || string.IsNullOrEmpty(issuer.PublicKeyCurveOid))
            return false;
        if (!EcPrimitives.TryCurveFromOid(issuer.PublicKeyCurveOid, out var curve))
            return false;
        return EcPrimitives.VerifyEcdsa(curve, issuer.PublicKeyBitString, hashAlg, tbs, sig);
    }

    private bool VerifyEd25519(DerCertificate issuer, ReadOnlySpan<byte> tbs, ReadOnlySpan<byte> sig)
    {
        if (!SignatureAlgorithmParametersRaw.IsEmpty)
            return false;
        if (issuer.PublicKeyAlgorithmOid != "1.3.101.112")
            return false;
        if (issuer.PublicKeyBitString.Length != 32 || sig.Length != 64)
            return false;
        return Ed25519.Verify(issuer.PublicKeyBitString, tbs, sig);
    }

    private static bool IsAbsentOrDerNull(ReadOnlySpan<byte> parameters) =>
        parameters.IsEmpty || (parameters.Length == 2 && parameters[0] == 0x05 && parameters[1] == 0x00);

    private static bool TryParsePssParameters(
        ReadOnlyMemory<byte> parametersRaw,
        out HashAlgorithmKind hashAlg,
        out int saltLength)
    {
        // If PSS parameters are omitted or NULL, default to SHA-256 with hash-sized salt (-1).
        if (IsAbsentOrDerNull(parametersRaw.Span))
        {
            hashAlg = HashAlgorithmKind.Sha256;
            saltLength = -1;
            return true;
        }

        // RFC 4055 §3.1 defaults inside an explicit RSASSA-PSS-params SEQUENCE
        hashAlg = HashAlgorithmKind.Sha1;
        var mgfHashAlg = HashAlgorithmKind.Sha1;
        saltLength = 20;

        var seq = Asn1Reader.ReadSingle(parametersRaw);
        if (!seq.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
            return false;

        var cursor = new Asn1Cursor(seq.Content);

        if (cursor.TryReadContextSpecific(0, true, out var hashCtx))
        {
            var innerCursor = new Asn1Cursor(hashCtx.Content);
            var hashAlgId = innerCursor.ReadUniversal(Asn1Tag.TagSequence, true);
            innerCursor.ExpectEnd();
            if (!TryParseHashAlgorithmIdentifier(hashAlgId, out hashAlg))
                return false;
        }

        if (cursor.TryReadContextSpecific(1, true, out var mgfCtx))
        {
            var innerCursor = new Asn1Cursor(mgfCtx.Content);
            var mgfAlgId = innerCursor.ReadUniversal(Asn1Tag.TagSequence, true);
            innerCursor.ExpectEnd();

            var (mgfOid, mgfParams) = ParseAlgorithmIdentifier(mgfAlgId);
            if (mgfOid != "1.2.840.113549.1.1.8" || mgfParams.IsEmpty)
                return false;

            var mgfHashSeq = Asn1Reader.ReadSingle(mgfParams);
            if (!mgfHashSeq.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
                return false;
            if (!TryParseHashAlgorithmIdentifier(mgfHashSeq, out mgfHashAlg))
                return false;
        }

        if (cursor.TryReadContextSpecific(2, true, out var saltCtx))
        {
            var innerCursor = new Asn1Cursor(saltCtx.Content);
            var saltNode = innerCursor.ReadUniversal(Asn1Tag.TagInteger, false);
            innerCursor.ExpectEnd();
            saltLength = Asn1Reader.ReadSmallInt(saltNode.ContentSpan);
            if (saltLength < 0)
                return false;
        }

        if (cursor.TryReadContextSpecific(3, true, out var trailerCtx))
        {
            var innerCursor = new Asn1Cursor(trailerCtx.Content);
            var trailerNode = innerCursor.ReadUniversal(Asn1Tag.TagInteger, false);
            innerCursor.ExpectEnd();
            if (Asn1Reader.ReadSmallInt(trailerNode.ContentSpan) != 1)
                return false;
        }

        cursor.ExpectEnd();
        return mgfHashAlg == hashAlg;
    }

    private static bool TryParseHashAlgorithmIdentifier(Asn1Node algIdNode, out HashAlgorithmKind hashAlg)
    {
        var (oid, paramRaw) = ParseAlgorithmIdentifier(algIdNode);
        if (!IsAbsentOrDerNull(paramRaw.Span))
        {
            hashAlg = default;
            return false;
        }

        switch (oid)
        {
            case "1.3.14.3.2.26":
                hashAlg = HashAlgorithmKind.Sha1;
                return true;
            case "2.16.840.1.101.3.4.2.1":
                hashAlg = HashAlgorithmKind.Sha256;
                return true;
            case "2.16.840.1.101.3.4.2.2":
                hashAlg = HashAlgorithmKind.Sha384;
                return true;
            case "2.16.840.1.101.3.4.2.3":
                hashAlg = HashAlgorithmKind.Sha512;
                return true;
            default:
                hashAlg = default;
                return false;
        }
    }

    private static (string Oid, ReadOnlyMemory<byte> ParametersRaw) ParseAlgorithmIdentifier(Asn1Node algNode)
    {
        var cursor = new Asn1Cursor(algNode.Content);
        var oidNode = cursor.ReadUniversal(Asn1Tag.TagObjectIdentifier, false);
        var oid = Asn1Reader.ReadOid(oidNode.ContentSpan);
        var parameters = cursor.HasRemaining ? cursor.ReadNext().HeaderAndContent : ReadOnlyMemory<byte>.Empty;
        cursor.ExpectEnd();
        return (oid, parameters);
    }

    private static List<(string Oid, string Value)> ParseName(Asn1Node nameNode)
    {
        var rdns = new List<(string Oid, string Value)>();
        var nameCursor = new Asn1Cursor(nameNode.Content);
        while (nameCursor.HasRemaining)
        {
            var setNode = nameCursor.ReadUniversal(Asn1Tag.TagSet, true);
            var setCursor = new Asn1Cursor(setNode.Content);
            while (setCursor.HasRemaining)
            {
                var atvNode = setCursor.ReadUniversal(Asn1Tag.TagSequence, true);
                var atvCursor = new Asn1Cursor(atvNode.Content);
                var oidNode = atvCursor.ReadUniversal(Asn1Tag.TagObjectIdentifier, false);
                var valNode = atvCursor.ReadNext();
                atvCursor.ExpectEnd();

                var oid = Asn1Reader.ReadOid(oidNode.ContentSpan);
                var value = ReadRdnValue(valNode);
                rdns.Add((oid, value));
            }
            setCursor.ExpectEnd();
        }
        nameCursor.ExpectEnd();
        return rdns;
    }

    private static string ReadRdnValue(Asn1Node node)
    {
        if (node.TagClass == Asn1TagClass.Universal && !node.IsConstructed)
        {
            switch (node.TagNumber)
            {
                case Asn1Tag.TagUtf8String:
                case Asn1Tag.TagPrintableString:
                case Asn1Tag.TagIA5String:
                case Asn1Tag.TagT61String:
                case Asn1Tag.TagBmpString:
                case Asn1Tag.TagUniversalString:
                case Asn1Tag.TagVisibleString:
                case Asn1Tag.TagNumericString:
                    return Asn1Reader.ReadStringValue(node);
            }
        }
        return "#" + Convert.ToHexString(node.HeaderAndContentSpan);
    }

    private static byte[] ParseOctetStringExtension(ReadOnlyMemory<byte> extValue)
    {
        var node = Asn1Reader.ReadSingle(extValue);
        if (!node.Tag.Matches(Asn1TagClass.Universal, false, Asn1Tag.TagOctetString))
            throw new FormatException("Expected OCTET STRING inside extension value.");
        return node.ContentSpan.ToArray();
    }

    private static X509KeyUsageFlagsLite ParseKeyUsage(ReadOnlyMemory<byte> extValue)
    {
        var node = Asn1Reader.ReadSingle(extValue);
        if (!node.Tag.Matches(Asn1TagClass.Universal, false, Asn1Tag.TagBitString))
            throw new FormatException("KeyUsage extension must be a BIT STRING.");

        var bits = Asn1Reader.ReadBitString(node.ContentSpan, out var unusedBits);
        var totalBits = bits.Length * 8 - unusedBits;
        var flags = X509KeyUsageFlagsLite.None;

        var limit = Math.Min(9, totalBits);
        for (var bitIndex = 0; bitIndex < limit; bitIndex++)
        {
            var byteIndex = bitIndex >> 3;
            var bitMask = 0x80 >> (bitIndex & 7);
            if ((bits[byteIndex] & bitMask) != 0)
                flags |= (X509KeyUsageFlagsLite)(1 << bitIndex);
        }
        return flags;
    }

    private static void ParseSan(ReadOnlyMemory<byte> extValue, List<string> dnsNames, List<IPAddress> ipAddresses)
    {
        var seq = Asn1Reader.ReadSingle(extValue);
        if (!seq.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
            throw new FormatException("SubjectAltName extension must be a SEQUENCE.");

        var cursor = new Asn1Cursor(seq.Content);
        while (cursor.HasRemaining)
        {
            var gn = cursor.ReadNext();
            if (gn.TagClass != Asn1TagClass.ContextSpecific)
                continue;

            if (!gn.IsConstructed && gn.TagNumber == 2) // dNSName [2] IMPLICIT IA5String
            {
                var bytes = gn.ContentSpan;
                for (var i = 0; i < bytes.Length; i++)
                {
                    if (bytes[i] == 0 || bytes[i] > 0x7F)
                        throw new FormatException("Invalid character in SubjectAltName dNSName.");
                }
                dnsNames.Add(Encoding.ASCII.GetString(bytes));
            }
            else if (!gn.IsConstructed && gn.TagNumber == 7) // iPAddress [7] IMPLICIT OCTET STRING
            {
                var bytes = gn.ContentSpan;
                if (bytes.Length != 4 && bytes.Length != 16)
                    throw new FormatException($"Invalid IP address length ({bytes.Length}) in SubjectAltName.");
                ipAddresses.Add(new IPAddress(bytes));
            }
        }
        cursor.ExpectEnd();
    }

    private static (bool IsCa, int? PathLenConstraint) ParseBasicConstraints(ReadOnlyMemory<byte> extValue)
    {
        var seq = Asn1Reader.ReadSingle(extValue);
        if (!seq.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
            throw new FormatException("BasicConstraints extension must be a SEQUENCE.");

        var cursor = new Asn1Cursor(seq.Content);
        var isCa = false;
        int? pathLen = null;

        if (cursor.TryPeekTag(out var nextTag) && nextTag.IsUniversal(Asn1Tag.TagBoolean))
        {
            var boolNode = cursor.ReadUniversal(Asn1Tag.TagBoolean, false);
            isCa = Asn1Reader.ReadBoolean(boolNode.ContentSpan);
        }

        if (cursor.TryPeekTag(out nextTag) && nextTag.IsUniversal(Asn1Tag.TagInteger))
        {
            var intNode = cursor.ReadUniversal(Asn1Tag.TagInteger, false);
            var val = Asn1Reader.ReadSmallInt(intNode.ContentSpan);
            if (val < 0)
                throw new FormatException("Negative pathLenConstraint in BasicConstraints.");
            pathLen = val;
        }

        cursor.ExpectEnd();
        return (isCa, pathLen);
    }

    private static NameConstraintsExt ParseNameConstraints(ReadOnlyMemory<byte> extValue, out bool fullyUnderstood)
    {
        var seq = Asn1Reader.ReadSingle(extValue);
        if (!seq.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
            throw new FormatException("NameConstraints extension must be a SEQUENCE.");

        fullyUnderstood = true;
        var permittedDns = new List<string>();
        var excludedDns = new List<string>();
        var permittedIps = new List<(byte[] Net, byte[] Mask)>();
        var excludedIps = new List<(byte[] Net, byte[] Mask)>();

        var cursor = new Asn1Cursor(seq.Content);
        if (cursor.TryReadContextSpecific(0, true, out var permittedNode))
        {
            if (!ParseGeneralSubtrees(permittedNode.Content, permittedDns, permittedIps))
                fullyUnderstood = false;
        }

        if (cursor.TryReadContextSpecific(1, true, out var excludedNode))
        {
            if (!ParseGeneralSubtrees(excludedNode.Content, excludedDns, excludedIps))
                fullyUnderstood = false;
        }

        cursor.ExpectEnd();

        return new NameConstraintsExt
        {
            PermittedDns = permittedDns,
            ExcludedDns = excludedDns,
            PermittedIpSubnets = permittedIps,
            ExcludedIpSubnets = excludedIps,
        };
    }

    private static bool ParseGeneralSubtrees(
        ReadOnlyMemory<byte> content,
        List<string> dnsList,
        List<(byte[] Net, byte[] Mask)> ipSubnets)
    {
        var fullyUnderstood = true;
        var cursor = new Asn1Cursor(content);
        while (cursor.HasRemaining)
        {
            var subtreeNode = cursor.ReadUniversal(Asn1Tag.TagSequence, true);
            var subCursor = new Asn1Cursor(subtreeNode.Content);
            var baseGn = subCursor.ReadNext();

            if (baseGn.TagClass == Asn1TagClass.ContextSpecific && !baseGn.IsConstructed)
            {
                switch (baseGn.TagNumber)
                {
                    case 2: // dNSName
                    {
                        var bytes = baseGn.ContentSpan;
                        for (var i = 0; i < bytes.Length; i++)
                        {
                            if (bytes[i] == 0 || bytes[i] > 0x7F)
                                throw new FormatException("Invalid character in NameConstraints dNSName.");
                        }
                        dnsList.Add(Encoding.ASCII.GetString(bytes));
                        break;
                    }
                    case 7: // iPAddress (addr || mask)
                    {
                        var bytes = baseGn.ContentSpan;
                        if (bytes.Length != 8 && bytes.Length != 32)
                            throw new FormatException($"Invalid IP NameConstraint length: {bytes.Length}.");
                        var half = bytes.Length / 2;
                        ipSubnets.Add((bytes.Slice(0, half).ToArray(), bytes.Slice(half, half).ToArray()));
                        break;
                    }
                    case 1: // rfc822Name
                    case 6: // uniformResourceIdentifier
                        break;
                    default:
                        fullyUnderstood = false;
                        break;
                }
            }
            else
            {
                fullyUnderstood = false;
            }

            // Optional minimum [0] / maximum [1]
            while (subCursor.HasRemaining)
                subCursor.ReadNext();
            subCursor.ExpectEnd();
        }
        cursor.ExpectEnd();
        return fullyUnderstood;
    }

    private static byte[]? ParseAuthorityKeyId(ReadOnlyMemory<byte> extValue)
    {
        var seq = Asn1Reader.ReadSingle(extValue);
        if (!seq.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
            throw new FormatException("AuthorityKeyIdentifier extension must be a SEQUENCE.");

        byte[]? keyId = null;
        var cursor = new Asn1Cursor(seq.Content);
        while (cursor.HasRemaining)
        {
            var field = cursor.ReadNext();
            if (field.Tag.Matches(Asn1TagClass.ContextSpecific, false, 0))
                keyId = field.ContentSpan.ToArray();
        }
        cursor.ExpectEnd();
        return keyId;
    }

    private static void ParseExtendedKeyUsage(ReadOnlyMemory<byte> extValue, List<string> ekus)
    {
        var seq = Asn1Reader.ReadSingle(extValue);
        if (!seq.Tag.Matches(Asn1TagClass.Universal, true, Asn1Tag.TagSequence))
            throw new FormatException("ExtendedKeyUsage extension must be a SEQUENCE.");

        var cursor = new Asn1Cursor(seq.Content);
        while (cursor.HasRemaining)
        {
            var oidNode = cursor.ReadUniversal(Asn1Tag.TagObjectIdentifier, false);
            ekus.Add(Asn1Reader.ReadOid(oidNode.ContentSpan));
        }
        cursor.ExpectEnd();
    }

    private static string FormatRdns(IReadOnlyList<(string Oid, string Value)> rdns)
    {
        if (rdns.Count == 0)
            return string.Empty;

        var parts = new string[rdns.Count];
        for (var i = 0; i < rdns.Count; i++)
        {
            var (oid, val) = rdns[i];
            var label = oid switch
            {
                "2.5.4.3" => "CN",
                "2.5.4.6" => "C",
                "2.5.4.7" => "L",
                "2.5.4.8" => "ST",
                "2.5.4.10" => "O",
                "2.5.4.11" => "OU",
                "2.5.4.5" => "SERIALNUMBER",
                "2.5.4.9" => "STREET",
                "2.5.4.17" => "POSTALCODE",
                "0.9.2342.19200300.100.1.25" => "DC",
                "1.2.840.113549.1.9.1" => "E",
                _ => oid,
            };
            parts[i] = $"{label}={val}";
        }
        return string.Join(", ", parts);
    }

    public override string ToString() => SubjectText;
}
