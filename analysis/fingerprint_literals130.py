import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

needles = ["Fingerprint", "HardwareConcurrency", "DeviceScaleFactor", "Profiles/", "--profile-directory",
           "user-data-dir", "--window-size"]

for n in needles:
    print("=== " + n)
    seen = set()
    count = 0
    for line in text.split("\n"):
        body = line.split("  ", 1)[-1]
        if n in body and body not in seen:
            seen.add(body)
            print("   ", body[:150])
            count += 1
            if count >= 5:
                break
    print()
