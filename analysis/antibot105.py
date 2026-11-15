import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

vendors = {
    "trustdecision": r"[A-Za-z0-9_\-\.]*trustdecision\.com[A-Za-z0-9_\-/\.{}$:?=&%]*",
    "kasada": r"[A-Za-z0-9_\-\.]*kasada[A-Za-z0-9_\-/\.]*",
    "perimeterx": r"[A-Za-z0-9_\-\.]*(?:perimeterx|px-cdn|pxchk|_px)[A-Za-z0-9_\-/\.]{0,40}",
    "datadome": r"[A-Za-z0-9_\-\.]*datadome[A-Za-z0-9_\-/\.]*",
    "akamai": r"[A-Za-z0-9_\-\.]*(?:akamai|_abck|bm_sz|sensor_data)[A-Za-z0-9_\-/\.]{0,40}",
    "cloudflare": r"[A-Za-z0-9_\-\.]*(?:challenges\.cloudflare|cf_chl|turnstile|__cf_bm)[A-Za-z0-9_\-/\.]{0,40}",
    "queueit": r"[A-Za-z0-9_\-\.]*(?:queue-it|queueit)[A-Za-z0-9_\-/\.]*",
    "hcaptcha": r"[A-Za-z0-9_\-\.]*(?:hcaptcha|recaptcha|funcaptcha|arkoselabs)[A-Za-z0-9_\-/\.]{0,40}",
}

for label, pat in vendors.items():
    hits = collections.Counter(re.findall(pat, text, re.IGNORECASE))
    print("=== %s (%d distinct)" % (label, len(hits)))
    for name, n in hits.most_common(8):
        print("   %-58s %d" % (name[:58], n))
    print()
