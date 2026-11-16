using System.Security.Cryptography;
using System.Text;

namespace Cybersole.Http;

/// <summary>
/// TLS 1.2 key derivation (RFC 5246 §5, §8.1): the PRF, master secret and
/// Finished verify_data. Pure functions — unit-tested against hmac reference values.
/// </summary>
public static class Tls12Prf
{
    /// <summary>PRF(secret, label, seed) = P_SHA256(secret, label + seed), truncated to length.</summary>
    public static byte[] Prf(byte[] secret, string label, byte[] seed, int length)
    {
        var labelBytes = Encoding.ASCII.GetBytes(label);
        var fullSeed = new byte[labelBytes.Length + seed.Length];
        labelBytes.CopyTo(fullSeed, 0);
        seed.CopyTo(fullSeed, labelBytes.Length);

        using var hmac = new HMACSHA256(secret);
        var result = new List<byte>(length);

        // A(1) = HMAC(secret, seed); A(i) = HMAC(secret, A(i-1))
        // output = HMAC(secret, A(1)+seed) || HMAC(secret, A(2)+seed) || ...
        var a = hmac.ComputeHash(fullSeed);
        while (result.Count < length)
        {
            var input = new byte[a.Length + fullSeed.Length];
            a.CopyTo(input, 0);
            fullSeed.CopyTo(input, a.Length);
            result.AddRange(hmac.ComputeHash(input));
            a = hmac.ComputeHash(a);
        }

        return result.Take(length).ToArray();
    }

    /// <summary>master_secret = PRF(pre_master_secret, "master secret", client_random + server_random)[48].</summary>
    public static byte[] MasterSecret(byte[] preMasterSecret, byte[] clientRandom, byte[] serverRandom)
    {
        var seed = new byte[clientRandom.Length + serverRandom.Length];
        clientRandom.CopyTo(seed, 0);
        serverRandom.CopyTo(seed, clientRandom.Length);
        return Prf(preMasterSecret, "master secret", seed, 48);
    }

    /// <summary>key_block = PRF(master_secret, "key expansion", server_random + client_random).</summary>
    public static byte[] KeyBlock(byte[] masterSecret, byte[] clientRandom, byte[] serverRandom, int length)
    {
        var seed = new byte[serverRandom.Length + clientRandom.Length];
        serverRandom.CopyTo(seed, 0);
        clientRandom.CopyTo(seed, serverRandom.Length);
        return Prf(masterSecret, "key expansion", seed, length);
    }

    /// <summary>Finished verify_data = PRF(master_secret, label, handshake_hash)[12].</summary>
    public static byte[] FinishedVerifyData(byte[] masterSecret, bool fromClient, byte[] handshakeHash)
        => Prf(masterSecret, fromClient ? "client finished" : "server finished", handshakeHash, 12);
}

/// <summary>ECDHE helpers producing TLS wire-format public keys.</summary>
public static class Ecdhe
{
    /// <summary>Create a P-256 key pair; returns the TLS uncompressed point (04 || X || Y).</summary>
    public static (ECDiffieHellman Key, byte[] PublicKey) CreateP256()
    {
        var key = ECDiffieHellman.Create(ECCurve.NamedCurves.nistP256);
        var parameters = key.ExportParameters(false);
        var publicKey = new byte[1 + parameters.Q.X!.Length + parameters.Q.Y!.Length];
        publicKey[0] = 0x04;
        parameters.Q.X.CopyTo(publicKey, 1);
        parameters.Q.Y.CopyTo(publicKey, 1 + parameters.Q.X.Length);
        return (key, publicKey);
    }

    /// <summary>Compute the shared secret against the server's uncompressed point.</summary>
    public static byte[] SharedSecret(ECDiffieHellman mine, byte[] serverPublicKey)
    {
        if (serverPublicKey.Length < 3 || serverPublicKey[0] != 0x04)
            throw new CryptographicException("expected an uncompressed EC point (0x04)");

        var half = (serverPublicKey.Length - 1) / 2;
        var x = serverPublicKey.AsSpan(1, half).ToArray();
        var y = serverPublicKey.AsSpan(1 + half, half).ToArray();

        using var server = ECDiffieHellman.Create(new ECParameters
        {
            Curve = ECCurve.NamedCurves.nistP256,
            Q = new ECPoint { X = x, Y = y },
        });

        return mine.DeriveKeyMaterial(server.PublicKey);
    }

    /// <summary>Create an X25519 key pair (BouncyCastle); returns the 32-byte public key.</summary>
    public static (Org.BouncyCastle.Crypto.Parameters.X25519PrivateKeyParameters Key, byte[] PublicKey) CreateX25519()
    {
        var key = new Org.BouncyCastle.Crypto.Parameters.X25519PrivateKeyParameters(
            new Org.BouncyCastle.Security.SecureRandom());
        return (key, key.GeneratePublicKey().GetEncoded());
    }

    /// <summary>X25519 shared secret against the server's 32-byte public key.</summary>
    public static byte[] SharedSecretX25519(
        Org.BouncyCastle.Crypto.Parameters.X25519PrivateKeyParameters mine, byte[] serverPublicKey)
    {
        var agreement = new Org.BouncyCastle.Crypto.Agreement.X25519Agreement();
        agreement.Init(mine);
        var secret = new byte[agreement.AgreementSize];
        agreement.CalculateAgreement(
            new Org.BouncyCastle.Crypto.Parameters.X25519PublicKeyParameters(serverPublicKey, 0), secret, 0);
        return secret;
    }
}
