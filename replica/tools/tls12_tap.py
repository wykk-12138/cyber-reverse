"""MITM tap: C# client -> this tap -> real Python ssl server.

Dumps every TLS record in both directions so we can see exactly which message a
real stack rejects.
"""
import datetime
import socket
import ssl
import sys
import threading
import time

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

LISTEN = int(sys.argv[1]) if len(sys.argv) > 1 else 14640
UPSTREAM = LISTEN + 1


def make_cert(path_cert, path_key):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    with open(path_key, "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM,
                                  serialization.PrivateFormat.TraditionalOpenSSL,
                                  serialization.NoEncryption()))
    with open(path_cert, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def start_ssl_server(port):
    cert, key = "tap_cert.pem", "tap_key.pem"
    make_cert(cert, key)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers("ECDHE-RSA-AES128-GCM-SHA256")
    ctx.load_cert_chain(cert, key)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(1)
    srv.settimeout(40)
    print(f"[ssl] listening {port}", flush=True)
    try:
        conn, _ = srv.accept()
        tls = ctx.wrap_socket(conn, server_side=True)
        print("[ssl] handshake OK", tls.version(), tls.cipher(), flush=True)
        tls.recv(4096)
        tls.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nhi")
        tls.close()
    except Exception as ex:
        print("[ssl] FAILED:", type(ex).__name__, ex, flush=True)
    srv.close()


NAMES = {20: "CCS", 21: "ALERT", 22: "HANDSHAKE", 23: "APPDATA"}


def dump(prefix, data):
    i = 0
    while i + 5 <= len(data):
        rtype = data[i]
        length = int.from_bytes(data[i + 3:i + 5], "big")
        body = data[i + 5:i + 5 + length]
        print(f"{prefix} {NAMES.get(rtype, hex(rtype))} len={length} body={body[:6].hex()}", flush=True)
        i += 5 + length
    if i < len(data):
        print(f"{prefix} trailing {len(data) - i}B {data[i:].hex()}", flush=True)


def pump(src, dst, tag):
    try:
        while True:
            chunk = src.recv(8192)
            if not chunk:
                break
            dump(tag, chunk)
            dst.sendall(chunk)
    except Exception:
        pass


def main():
    threading.Thread(target=start_ssl_server, args=(UPSTREAM,), daemon=True).start()
    time.sleep(2)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", LISTEN))
    srv.listen(1)
    srv.settimeout(40)
    print(f"[tap] {LISTEN} -> {UPSTREAM}", flush=True)

    client, _ = srv.accept()
    upstream = socket.create_connection(("127.0.0.1", UPSTREAM))
    client.settimeout(20)
    upstream.settimeout(20)

    t1 = threading.Thread(target=pump, args=(client, upstream, "[C>S]"))
    t2 = threading.Thread(target=pump, args=(upstream, client, "[S>C]"))
    t1.start()
    t2.start()
    t1.join(25)
    t2.join(25)
    client.close()
    upstream.close()
    srv.close()


if __name__ == "__main__":
    main()
