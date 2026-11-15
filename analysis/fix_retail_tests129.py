import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\RetailApiFamiliesTests.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the combined total follows the family's growth
t = t.replace("        Assert.Equal(29, RetailApiFamilies.All.Count);",
              "        Assert.Equal(30, RetailApiFamilies.All.Count);   // R129: 13 + 17", 1)
t = t.replace("        Assert.Equal(29, RetailApiFamilies.All.Distinct().Count());",
              "        Assert.Equal(30, RetailApiFamilies.All.Distinct().Count());", 1)

# 2) the shape assertion: one endpoint deliberately sits beside the BFF rather than under it
old = '''        Assert.All(RetailApiFamilies.JohnLewisBff.All,
            u => Assert.StartsWith("https://checkout.johnlewis.com/bff/v", u));'''
new = '''        // twelve sit under bff/, one sits beside it (the guest login callback, R129)
        Assert.All(RetailApiFamilies.JohnLewisBff.All.Where(u => u != RetailApiFamilies.JohnLewisBff.GuestLoginCallback),
            u => Assert.StartsWith("https://checkout.johnlewis.com/bff/v", u));
        Assert.StartsWith("https://checkout.johnlewis.com/callback/login/guest",
            RetailApiFamilies.JohnLewisBff.GuestLoginCallback);'''

if old in t:
    t = t.replace(old, new, 1)
else:
    print("warning: starts-with anchor not found")

if "using System.Linq;" not in t:
    t = "using System.Linq;\n" + t

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("retail family assertions updated")
