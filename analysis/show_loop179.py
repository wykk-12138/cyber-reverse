import io

t = io.open(r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\EngineParity.cs",
            encoding="utf-8").read()

i = t.find("'Error', 'TypeError'")
print(t[i - 400:i + 1800])
