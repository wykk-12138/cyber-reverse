import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\SettingsDialogSingleSourceTests.cs"
t = io.open(p, encoding="utf-8").read()

# 'Content = "Add"' with single quotes is a char literal in C# — needs double quotes.
t = t.replace("""Assert.Contains('Content = "Add"', source);""",
              """Assert.Contains("Content = \\"Add\\"", source);""")
t = t.replace("""Assert.Contains('Content = "Search"', source);""",
              """Assert.Contains("Content = \\"Search\\"", source);""")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("quote literals fixed")
