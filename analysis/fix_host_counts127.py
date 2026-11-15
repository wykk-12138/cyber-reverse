import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ServiceHostTests.cs"
t = io.open(p, encoding="utf-8").read()

# R127: Scheels mobile dropped from three endpoints to two, and the app map from five steps to four.
old1 = "        Assert.Equal(3, ServiceHosts.ScheelsMobile.All.Count);"
new1 = "        Assert.Equal(2, ServiceHosts.ScheelsMobile.All.Count);"
if old1 in t:
    t = t.replace(old1, new1, 1)

old2 = "        Assert.Equal(5, ServiceHosts.DualApi.AppSteps.Count);"
new2 = "        Assert.Equal(4, ServiceHosts.DualApi.AppSteps.Count);   // R127: SubmitOrderApp unmapped"
if old2 in t:
    t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("counts follow the correction")
