import io, json, base64, datetime, os

def b64url(s):
    s += '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode())

cands = [r"C:\Users\wykk\AppData\Roaming\Cybersole\settings.json"]
for p in cands:
    if not os.path.exists(p):
        print("missing:", p); continue
    d = json.loads(io.open(p, encoding='utf-8').read())
    print("path:", p)
    print("top-level keys:", sorted(d.keys())[:20])
    b = d.get("bearer") or d.get("Bearer")
    print("bearer present:", bool(b), "| length:", len(b) if b else 0)
    if b and b.count('.') == 2:
        h, pl, sig = b.split('.')
        try:
            head = json.loads(b64url(h)); pay = json.loads(b64url(pl))
            print("  header:", {k: head[k] for k in head if k in ('alg','typ','kid')})
            print("  claim names:", sorted(pay.keys()))
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            for k in ('iat','nbf','exp'):
                if k in pay:
                    print("  %s:" % k, datetime.datetime.fromtimestamp(pay[k], datetime.timezone.utc).isoformat(), "| delta_hours: %.1f" % ((pay[k]-now)/3600))
        except Exception as e:
            print("  jwt decode failed:", type(e).__name__, e)
    lic = d.get("license")
    print("license present:", bool(lic), "| type:", type(lic).__name__, "| len:", len(lic) if isinstance(lic, str) else (len(json.dumps(lic)) if lic else 0))
