import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

needles = ["SaleRegistration", "saleRegistration", "raffle", "Raffle", "draw", "Draw",
           "signup", "Signup", "signUp"]

seen = set()
for line in lines:
    body = line.split("  ", 1)[-1]
    if not any(n in body for n in needles):
        continue
    if body in seen:
        continue
    seen.add(body)
    print("  ", body[:160])
