import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheGroupDialogLabelsAreTheImagesLabels()
    {
        // the image capitalises these; the dialog used to print "Monitor delay" / "Cloudflare solver"
        Assert.Equal("Monitor Delay", TaskGroupView.MonitorDelayLabel);
        Assert.Equal("Error Delay", TaskGroupView.ErrorDelayLabel);
        Assert.Equal("Total Checkout Limit", TaskGroupView.TotalCheckoutLimitLabel);
        Assert.Equal("Resetting at", TaskGroupView.ResettingAtLabel);
        Assert.Equal("Captcha Solving Source", TaskGroupView.CaptchaSourceLabel);
        Assert.Equal("Cloudflare Solver", TaskGroupView.CloudflareSolverLabel);
        Assert.Equal("Webhook Filter", TaskGroupView.WebhookFilterLabel);
    }

    [Fact]
    public void TheGroupTooltipsAndPlaceholdersAreTheImagesWords()
    {
        Assert.Equal("When toggled, both monitor and retry delays will stay the same", TaskGroupView.LinkTooltip);
        Assert.Equal("Select source", TaskGroupView.CaptchaSourceSelect);
        Assert.Equal("Select webhook(s)", TaskGroupView.WebhookFilterSelect);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('task group copy tests appended')
