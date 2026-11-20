using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;

namespace Cybersole.Http.X509;

/// <summary>
/// Pure-managed trusted root certificate store matching <c>Cybersole.Http.X509.RootCertificates.bin</c>.
/// Reads length-prefixed <c>[uint32 BE length][DER bytes]</c> bundles and indexes certificates by
/// subject distinguished name and SubjectKeyIdentifier / public-key SHA-256 for chain verification.
/// </summary>
public sealed class RootCertificateStore
{
    public const string ResourceName = "Cybersole.Http.X509.RootCertificates.bin";

    private static readonly Lazy<RootCertificateStore> SharedInstance =
        new(LoadDefault, isThreadSafe: true);

    private readonly List<X509Certificate2> _certificates = new();
    private readonly Dictionary<string, List<X509Certificate2>> _bySubject = new(StringComparer.Ordinal);
    private readonly Dictionary<string, X509Certificate2> _byKeyHash = new(StringComparer.OrdinalIgnoreCase);

    public static RootCertificateStore Shared => SharedInstance.Value;
    public int Count => _certificates.Count;

    public void Add(X509Certificate2 cert)
    {
        ArgumentNullException.ThrowIfNull(cert);
        _certificates.Add(cert);

        var subjectKey = cert.SubjectName.Name;
        if (!_bySubject.TryGetValue(subjectKey, out var list))
        {
            list = new List<X509Certificate2>();
            _bySubject[subjectKey] = list;
        }
        list.Add(cert);

        foreach (var ext in cert.Extensions)
        {
            if (ext is X509SubjectKeyIdentifierExtension ski && !string.IsNullOrEmpty(ski.SubjectKeyIdentifier))
                _byKeyHash[ski.SubjectKeyIdentifier] = cert;
        }

        var spkiHash = Convert.ToHexString(SHA256.HashData(cert.PublicKey.ExportSubjectPublicKeyInfo()));
        _byKeyHash[spkiHash] = cert;
    }

    public IReadOnlyList<X509Certificate2> FindBySubject(string subject) =>
        _bySubject.TryGetValue(subject, out var list) ? list : Array.Empty<X509Certificate2>();

    public X509Certificate2? FindByKeyHash(string keyHash) =>
        _byKeyHash.TryGetValue(keyHash, out var cert) ? cert : null;

    /// <summary>
    /// Parse a stream formatted as <c>[uint32 BE length][DER bytes]</c> records.
    /// </summary>
    public static RootCertificateStore LoadFromBundleStream(Stream stream)
    {
        ArgumentNullException.ThrowIfNull(stream);
        var store = new RootCertificateStore();
        Span<byte> lenBuf = stackalloc byte[4];
        while (ReadExact(stream, lenBuf))
        {
            var len = BinaryPrimitives.ReadUInt32BigEndian(lenBuf);
            if (len == 0 || len > 16 * 1024 * 1024)
                throw new InvalidDataException($"Invalid X509 DER record length: {len}");
            var der = new byte[len];
            if (!ReadExact(stream, der))
                throw new EndOfStreamException("Truncated DER certificate record in root bundle.");
            store.Add(new X509Certificate2(der));
        }
        return store;
    }

    public static void WriteBundleStream(Stream stream, IEnumerable<X509Certificate2> certificates)
    {
        ArgumentNullException.ThrowIfNull(stream);
        ArgumentNullException.ThrowIfNull(certificates);
        Span<byte> lenBuf = stackalloc byte[4];
        foreach (var cert in certificates)
        {
            var raw = cert.RawData;
            BinaryPrimitives.WriteUInt32BigEndian(lenBuf, (uint)raw.Length);
            stream.Write(lenBuf);
            stream.Write(raw, 0, raw.Length);
        }
    }

    public static RootCertificateStore LoadDefault()
    {
        var asm = typeof(RootCertificateStore).Assembly;
        using var embedded = asm.GetManifestResourceStream(ResourceName);
        if (embedded is not null)
            return LoadFromBundleStream(embedded);

        var store = new RootCertificateStore();
        foreach (var location in new[] { StoreLocation.LocalMachine, StoreLocation.CurrentUser })
        {
            try
            {
                using var sys = new X509Store(StoreName.Root, location);
                sys.Open(OpenFlags.ReadOnly);
                foreach (var cert in sys.Certificates)
                    store.Add(new X509Certificate2(cert.RawData));
            }
            catch
            {
                // Best-effort fallback on constrained hosts
            }
        }
        return store;
    }

    /// <summary>
    /// Verify a leaf certificate (with optional intermediates) against this root store's indexed trust anchors.
    /// </summary>
    public bool VerifyChain(X509Certificate2 leaf, IReadOnlyList<X509Certificate2>? intermediates = null, DateTime? atUtc = null)
    {
        ArgumentNullException.ThrowIfNull(leaf);
        var now = (atUtc ?? DateTime.UtcNow).ToLocalTime();

        using var chain = new X509Chain();
        chain.ChainPolicy.RevocationMode = X509RevocationMode.NoCheck;
        chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;
        chain.ChainPolicy.VerificationTime = now;
        foreach (var root in _certificates)
            chain.ChainPolicy.CustomTrustStore.Add(root);
        if (intermediates is not null)
        {
            foreach (var mid in intermediates)
                chain.ChainPolicy.ExtraStore.Add(mid);
        }

        return chain.Build(leaf);
    }

    private static bool ReadExact(Stream stream, Span<byte> target)
    {
        var offset = 0;
        while (offset < target.Length)
        {
            var n = stream.Read(target[offset..]);
            if (n == 0)
                return offset == 0 ? false : throw new EndOfStreamException();
            offset += n;
        }
        return true;
    }
}
