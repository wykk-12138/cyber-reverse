import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SessionPayloadBuilder.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            ["time-local"] = inputs.Now.ToString("d-M-yyyy, HH:mm:ss", CultureInfo.InvariantCulture),'''

new = '''            // The sample's time-local is the host's clock, not UTC: 1778830875801 is 07:41:15 UTC and the
            // sample says 09:41:15, because the host reports getTimezoneOffset() == -120. So the local
            // string is formatted from the same instant shifted by the negated offset — the two keys must
            // agree or the payload contradicts itself about when it was built (R153).
            ["time-local"] = inputs.Now
                .ToOffset(TimeSpan.FromMinutes(-inputs.TimezoneOffsetMinutes))
                .ToString("d-M-yyyy, HH:mm:ss", CultureInfo.InvariantCulture),'''

if old not in t:
    raise SystemExit("time-local anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("time-local is formatted in the claimed zone")
