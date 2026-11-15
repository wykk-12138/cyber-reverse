import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\NikeFlow.cs"
t = io.open(p, encoding="utf-8").read()

# CartUrl was static when the marketplace was a const; the country is per instance now.
old = '''    private static string CartUrl() =>
        $"https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simpified";'''
old = '''    private static string CartUrl() =>
        $"https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified";'''
new = '''    private string CartUrl() =>
        $"https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified";'''
if old not in t:
    raise SystemExit("CartUrl anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("CartUrl is an instance method now")
