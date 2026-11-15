"""A real TLS 1.2 server (Python ssl) with a self-signed cert.

Used to check whether the C# client works against a standard TLS implementation
(as opposed to the hand-written mock that only verifies the Finished record).
"""
import datetime
import socket
import ssl
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 14443


def make_cert(path_cert: str, path_key: str):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    with open(path_key, "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()))
    with open(path_cert, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


cert_path = "mock_cert.pem"
key_path = "mock_key.pem"
make_cert(cert_path, key_path)

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.maximum_version = ssl.TLSVersion.TLSv1_2
ctx.set_ciphers("ECDHE-RSA-AES128-GCM-SHA256")
ctx.load_cert_chain(cert_path, key_path)

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", PORT))
srv.listen(1)
srv.settimeout(30)
print(f"ssl server listening on {PORT}", flush=True)

conn, _ = srv.accept()
try:
    tls = ctx.wrap_socket(conn, server_side=True)
    print("handshake OK, cipher:", tls.cipher(), "version:", tls.version(), flush=True)
    data = tls.recv(4096)
    print("request bytes:", len(data), flush=True)
    tls.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 12\r\nConnection: close\r\n\r\nhello world\n")
    tls.close()
except Exception as ex:  # noqa: BLE001
    print("handshake FAILED:", type(ex).__name__, ex, flush=True)

srv.close()
