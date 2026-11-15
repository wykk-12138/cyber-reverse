import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\NotificationsPageTests.cs"
t = io.open(p, encoding="utf-8").read()

t = t.replace("using Cybersole.Core.Settings;",
              "using Cybersole.Core.Settings;\nusing Cybersole.Core.Store;\nusing Cybersole.Http;", 1)

t = t.replace('''    private static Cybersole.Http.NetClient TestNet() =>
        Services.TestNetClient.Create();''',
              '''    private static NetClient TestNet() => new();''')

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("usings fixed")
