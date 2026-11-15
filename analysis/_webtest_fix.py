import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\WebhookCreatorLabelTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('[InlineData("probe", "https://discord.com/api/webhooks", "Enter valid webhook")]',
              '[InlineData("probe", "", "Enter valid webhook")]   // empty box: the URL text on screen is the watermark, not a value')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test case corrected (placeholder is not a value)')
