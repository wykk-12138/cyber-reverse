import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('        new ReleaseGuideView(_releaseServices, _release) { }.Show(owner);',
'''        Views.Common.ViewHostModal.Show(this, "Buying guide", new ReleaseGuideView(_releaseServices, _release));''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ShowGuide uses the shared modal host (ReleaseGuideView is a UserControl)')
