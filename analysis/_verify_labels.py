import io
rows = [
 ("PROXY GROUPS", "ProxyView.cs"), ("Search groups", "ProxyView.cs"), ("No Proxies Loaded", "ProxyGrid.cs"),
 ("current download", "ProxyView.cs"), ("current upload", "ProxyView.cs"),
 ("Add some proxies to get started", "ProxyGrid.cs"), ("PROFILE GROUPS", "ProfileViews.cs"),
 ("No Profiles Loaded", "src/Cybersole.Ui/Views/BillingView.cs"), ("CSV Editor", "src/Cybersole.Ui/Views/BillingView.cs"),
 ("Search profiles", "src/Cybersole.Ui/Views/BillingView.cs"), ("Add Profile", "src/Cybersole.Ui/Views/BillingView.cs"),
 ("Clear Profiles", "src/Cybersole.Ui/Views/BillingView.cs"), ("Add some profiles to get started", "src/Cybersole.Ui/Views/BillingView.cs"),
 ("Card Holder", "src/Cybersole.Ui/Views/BillingView.cs"),
]
R = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views'
for name, f in rows:
    path = f if f.startswith('src') else (r'Cybersole.Ui/Views'.replace('Cybersole.Ui/Views','') + f)
    p = (R.replace('\\Views','') + '/' + f) if f.startswith('src') else (R + '/' + f)
    try:
        t = io.open(p, encoding='utf-8').read()
        print('%-32s %s' % (name, 'ok' if name in t else 'MISS'))
    except FileNotFoundError:
        print('%-32s file missing: %s' % (name, p))
