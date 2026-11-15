import io, re
# 1) the profile fields that are declared but never referenced: Delivery joins the recorded set
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ProfileProxyBindingTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '"Mobile", "MobilePrefix", "Region", "StreetSecondLine", "StreetThirdLine",'
new = '"Delivery", "Mobile", "MobilePrefix", "Region", "StreetSecondLine", "StreetThirdLine",'
assert old in t, 'expected set not found'
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Delivery recorded in the unreferenced set')

# 2) ceiling = the measured 57
p2 = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t2 = io.open(p2, encoding='utf-8').read()
t2 = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 57;', t2)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ceiling 58 -> 57')
