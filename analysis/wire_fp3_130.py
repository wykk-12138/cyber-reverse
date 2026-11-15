import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# Undo the concat attempt: the stealth script is one raw string literal and must stay one. The two
# hardware values are substituted after the fact instead.
old = (
    "              Object.defineProperty(N, 'hardwareConcurrency', { get: () => \" +\n"
    "                fingerprint.HardwareConcurrency + @\", configurable: true });\n"
    "              Object.defineProperty(N, 'deviceMemory', { get: () => \" +\n"
    "                fingerprint.DeviceMemory + @\", configurable: true });"
)
new = '''              Object.defineProperty(N, 'hardwareConcurrency', { get: () => __HC__, configurable: true });
              Object.defineProperty(N, 'deviceMemory', { get: () => __DM__, configurable: true });'''

if old not in t:
    raise SystemExit("concat block not found")
t = t.replace(old, new, 1)

# a single substitution point, so the raw literal stays a literal
old_inject = "                source = StealthScript,"
new_inject = ("                source = StealthScript\n"
              "                    .Replace(\"__HC__\", fingerprint.HardwareConcurrency.ToString())\n"
              "                    .Replace(\"__DM__\", fingerprint.DeviceMemory.ToString()),")
if old_inject not in t:
    raise SystemExit("injection anchor missing")
t = t.replace(old_inject, new_inject, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the raw script stays raw; values substituted at injection")
