import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the window size follows the profile's fingerprint instead of being fixed
old_win = '            "--window-size=1280,900",'
new_win = '            fingerprint.WindowSizeArgument(),'
if old_win not in t:
    raise SystemExit("window-size anchor missing")
t = t.replace(old_win, new_win, 1)

# 2) hardware hints come from the fingerprint, and the two hardcoded values are gone
old_hw = '''              Object.defineProperty(N, 'hardwareConcurrency', { get: () => 8, configurable: true });
              Object.defineProperty(N, 'deviceMemory', { get: () => 8, configurable: true });'''
new_hw = '''              // R130: per-profile, not 8/8 for every run — two sessions from one install used to
              // report identical hardware, which is the first thing a fingerprint check looks at.
              Object.defineProperty(N, 'hardwareConcurrency', { get: () => __HC__, configurable: true });
              Object.defineProperty(N, 'deviceMemory', { get: () => __DM__, configurable: true });'''
if old_hw not in t:
    raise SystemExit("hardware anchor missing")
t = t.replace(old_hw, new_hw, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("window size and hardware hints now come from a fingerprint")
