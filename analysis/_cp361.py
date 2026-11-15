import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    public int Priority { get; set; }
    public bool Enabled { get; set; }
    public int Concurrency { get; set; } = 10;
}'''
new = '''    public int Priority { get; set; }
    public bool Enabled { get; set; }
    public int Concurrency { get; set; } = 10;

    // R361: the binding table names three more fields on this record; CloudflareSolverConfig already had two of them,
    // CaptchaProvider had none, so the two lists could not be shown the same way.
    public int Count { get; set; }
    public bool BalanceSupported { get; set; }
    public bool IsFetchingBalance { get; set; }
}'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('CaptchaProvider gains Count / BalanceSupported / IsFetchingBalance')
