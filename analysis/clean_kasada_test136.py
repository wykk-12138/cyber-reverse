import io

# The file was written by a tool that mangled the header comment; rewrite the opening cleanly.
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KasadaStrategyTests.cs"
t = io.open(p, encoding="utf-8").read()

if t.startswith("using Cybersole.Stores.Flows;\nusing Cybersole.Stores.Scripts;"):
    print("header already clean")
else:
    # keep only from the first 'using' or 'namespace' onward, then prepend the two usings
    start = t.find("namespace Cybersole.Tests")
    doc = t[t.rfind("/// <summary>", 0, start):start] if "/// <summary>" in t[:start] else ""
    body = t[start:]
    io.open(p, "w", encoding="utf-8", newline="").write(
        "using Cybersole.Stores.Flows;\nusing Cybersole.Stores.Scripts;\nusing Xunit;\nusing Xunit.Abstractions;\n\n"
        + doc + body)
    print("header rebuilt")
