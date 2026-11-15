"""Minimal TLS 1.2 server with optional extended_master_secret (RFC 7627).

Used to validate the C# client's EMS path: replies ServerHello (+EMS) + empty
Certificate + ServerKeyExchange(X25519) + ServerHelloDone, derives the master
secret and tries to decrypt the client's Finished.
"""
import hashlib
import hmac
import socket
import struct
import sys

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 14610
USE_EMS = (len(sys.argv) < 3) or (sys.argv[2] != "noems")


def prf(secret: bytes, label: str, seed: bytes, length: int) -> bytes:
    seed = label.encode() + seed
    out = b""
    a = seed
    while len(out) < length:
        a = hmac.new(secret, a, hashlib.sha256).digest()
        out += hmac.new(secret, a + seed, hashlib.sha256).digest()
    return out[:length]


def recv_record(conn):
    header = b""
    while len(header) < 5:
        chunk = conn.recv(5 - len(header))
        if not chunk:
            return None
        header += chunk
    length = struct.unpack(">H", header[3:5])[0]
    payload = b""
    while len(payload) < length:
        chunk = conn.recv(length - len(payload))
        if not chunk:
            return None
        payload += chunk
    return header[0], payload


def handshake_msg(msg_type: int, body: bytes) -> bytes:
    return bytes([msg_type]) + len(body).to_bytes(3, "big") + body


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", PORT))
    srv.listen(1)
    srv.settimeout(30)
    print(f"listening on {PORT} (EMS={USE_EMS})", flush=True)

    conn, _ = srv.accept()
    conn.settimeout(15)

    rtype, ch_payload = recv_record(conn)
    client_random = ch_payload[6:38]
    transcript = bytearray(ch_payload)
    print("client_random", client_random.hex().upper(), flush=True)

    priv = X25519PrivateKey.generate()
    server_pub = priv.public_key().public_bytes_raw()
    server_random = bytes.fromhex("11223344556677889900AABBCCDDEEFF" * 2)

    ext = b"\x00\x17\x00\x00" if USE_EMS else b""
    sh_body = (b"\x03\x03" + server_random + b"\x00" + b"\x00\x2b" + b"\x00" +
               len(ext).to_bytes(2, "big") + ext)
    sh = handshake_msg(0x02, sh_body)
    conn.sendall(b"\x16\x03\x03" + len(sh).to_bytes(2, "big") + sh)
    transcript += sh

    cert = handshake_msg(0x0B, b"\x00\x00\x00")
    conn.sendall(b"\x16\x03\x03" + len(cert).to_bytes(2, "big") + cert)
    transcript += cert

    ske_body = b"\x03" + b"\x00\x1d" + bytes([len(server_pub)]) + server_pub + b"\x04\x03" + b"\x00\x00"
    ske = handshake_msg(0x0C, ske_body)
    conn.sendall(b"\x16\x03\x03" + len(ske).to_bytes(2, "big") + ske)
    transcript += ske

    shd = handshake_msg(0x0E, b"")
    conn.sendall(b"\x16\x03\x03" + len(shd).to_bytes(2, "big") + shd)
    transcript += shd
    print("server flight sent", flush=True)

    rec = recv_record(conn)
    if rec is None or rec[0] != 0x16:
        print("expected ClientKeyExchange")
        return
    cke = rec[1]
    transcript += cke
    pub_len = cke[4]
    client_pub = cke[5:5 + pub_len]
    print("client_pub", client_pub.hex().upper(), flush=True)

    secret = priv.exchange(X25519PublicKey.from_public_bytes(client_pub))
    print("pre_master", secret.hex().upper(), flush=True)

    if USE_EMS:
        session_hash = hashlib.sha256(bytes(transcript)).digest()
        master = prf(secret, "extended master secret", session_hash, 48)
        print("master (EMS)", master.hex().upper(), flush=True)
    else:
        master = prf(secret, "master secret", client_random + server_random, 48)
        print("master (legacy)", master.hex().upper(), flush=True)

    key_block = prf(master, "key expansion", server_random + client_random, 40)
    client_key = key_block[:16]
    client_iv = key_block[32:36]

    rec = recv_record(conn)
    if rec is None or rec[0] != 0x14:
        print("expected CCS")
        return
    rec = recv_record(conn)
    if rec is None or rec[0] != 0x16:
        print("expected Finished")
        return

    payload = rec[1]
    explicit = payload[:8]
    cipher = payload[8:-16]
    tag = payload[-16:]
    aad = (0).to_bytes(8, "big") + bytes([0x16, 0x03, 0x03]) + len(cipher).to_bytes(2, "big")
    nonce = client_iv + explicit

    try:
        plain = AESGCM(client_key).decrypt(nonce, cipher + tag, aad)
        print("finished decrypted OK, verify_data =", plain.hex().upper(), flush=True)
        expected = prf(master, "client finished", hashlib.sha256(bytes(transcript)).digest(), 12)
        print("expected verify_data            =", expected.hex().upper(), flush=True)
        print("verify match:", plain == expected, flush=True)
    except Exception as ex:  # noqa: BLE001
        print("finished decrypt FAILED:", ex, flush=True)

    conn.close()
    srv.close()


if __name__ == "__main__":
    main()
