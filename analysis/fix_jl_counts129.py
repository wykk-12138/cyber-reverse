import io

# R129 added GuestLoginCallback to the John Lewis family: 12 -> 13 endpoints, so two counts move and
# the "unused endpoints" list gains one.
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\RetailApiFamiliesTests.cs"
t1 = io.open(p1, encoding="utf-8").read()
t1 = t1.replace("Assert.Equal(12, RetailApiFamilies.JohnLewisBff.All.Count);",
                "Assert.Equal(13, RetailApiFamilies.JohnLewisBff.All.Count);   // R129: guest login callback", 1)
io.open(p1, "w", encoding="utf-8", newline="").write(t1)
print("john lewis family count: 13")

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JohnLewisStepMapTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

old = '''        Assert.Equal(3, JohnLewisStepMap.UnusedEndpoints.Count);'''
new = '''        // four, not three: R129 added the guest login callback, which no step names
        Assert.Equal(4, JohnLewisStepMap.UnusedEndpoints.Count);'''
if old in t2:
    t2 = t2.replace(old, new, 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("unused endpoints: 4")
