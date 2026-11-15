"""Capture TLS ClientHellos and print cipher suites + extension types (one JSON per line)."""
import json
import socket
import struct
import sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 14443
count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0

GREASE = {0x0A0A, 0x1A1A, 0x2A2A, 0x3A3A, 0x4A4A, 0x5A5A,
          0x6A6A, 0x7A7A, 0x8A8A, 0x9A9A, 0xAAAA, 0xBABA,
          0xCACA, 0xDADA, 0xEAEA, 0xFAFA}


def parse(data):
    out = {"bytes": len(data)}
    try:
        body = data[5:]
        p = 4 + 2
        p += 32
        sid_len = body[p]; p += 1 + sid_len
        cs_len = struct.unpack(">H", body[p:p + 2])[0]; p += 2
        suites = [struct.unpack(">H", body[p + i:p + i + 2])[0] for i in range(0, cs_len, 2)]
        p += cs_len
        comp_len = body[p]; p += 1 + comp_len
        ext_types, sni = [], None
        if p + 2 <= len(body):
            ext_len = struct.unpack(">H", body[p:p + 2])[0]; p += 2
            end = min(len(body), p + ext_len)
            while p + 4 <= end:
                etype = struct.unpack(">H", body[p:p + 2])[0]
                elen = struct.unpack(">H", body[p + 2:p + 4])[0]
                ext_types.append(etype)
                if etype == 0 and elen > 5:
                    try:
                        q = p + 4 + 5
                        name_len = struct.unpack(">H", body[q - 2:q])[0]
                        sni = body[q:q + name_len].decode("ascii", "replace")
                    except Exception:
                        pass
                p += 4 + elen
        out.update({
            "cipher_count": len(suites),
            "cipher_suites": [f"0x{c:04X}" for c in suites],
            "grease_cipher": any(c in GREASE for c in suites),
            "extension_count": len(ext_types),
            "extensions": [f"0x{e:04X}" for e in ext_types],
            "grease_extension": any(e in GREASE for e in ext_types),
            "sni": sni,
        })
    except Exception as ex:  # noqa: BLE001
        out["parse_error"] = str(ex)
        out["raw_hex"] = data[:100].hex()
    return out


srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", port))
srv.listen(16)
srv.settimeout(timeout)
print(f"listening on 127.0.0.1:{port} for {count} connections", flush=True)

for idx in range(count):
    try:
        conn, _ = srv.accept()
    except socket.timeout:
        print(json.dumps({"index": idx, "error": "timeout"}))
        break
    conn.settimeout(5)
    data = b""
    try:
        while len(data) < 5:
            chunk = conn.recv(8192)
            if not chunk:
                break
            data += chunk
        if len(data) >= 5:
            rec_len = struct.unpack(">H", data[3:5])[0]
            while len(data) < 5 + rec_len:
                chunk = conn.recv(8192)
                if not chunk:
                    break
                data += chunk
    finally:
        conn.close()

    result = parse(data)
    result["index"] = idx
    print(json.dumps(result), flush=True)

srv.close()
