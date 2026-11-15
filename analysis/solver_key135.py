import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumKasadaSolver.cs"
t = io.open(p, encoding="utf-8").read()

# the result should carry the key from the bridge even when no session was passed
old = '''            if (session is not null)
            {
                BrowserIdentity.RecordProfile(session, bridge.ProfilePath,
                    utcOffsetMinutes: BrowserIdentity.TimeZoneOffset(session),
                    userAgentAlreadySent: true);
            }'''

new = '''            ProfileKey = bridge.ProfilePath;

            if (session is not null)
            {
                BrowserIdentity.RecordProfile(session, bridge.ProfilePath,
                    utcOffsetMinutes: BrowserIdentity.TimeZoneOffset(session),
                    userAgentAlreadySent: true);
            }'''

if old not in t:
    raise SystemExit("record anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("ProfileKey set from the bridge")
