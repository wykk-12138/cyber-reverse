import io, re, os

src = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(src, encoding="utf-8", errors="replace").read()

hosts = sorted({h.lower() for h in re.findall(r"[a-z0-9][a-z0-9\-]*\.myshopify\.com", text, re.IGNORECASE)})

out = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\shopify_hosts.txt"
io.open(out, "w", encoding="utf-8", newline="").write("\n".join(hosts) + "\n")
print("hosts written:", len(hosts))
print("first 5:", hosts[:5])

# how many does the replica already know?
reg = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Modules\Registry.cs"
rtext = io.open(reg, encoding="utf-8").read().lower()
known = [h for h in hosts if h.split(".")[0] in rtext]
print("replica mentions %d of them by subdomain" % len(known))
