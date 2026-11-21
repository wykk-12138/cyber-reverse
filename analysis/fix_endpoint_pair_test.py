"""Make the endpoint pair test compile: Warhammer's host is private, the Flex endpoint is public."""

import io

TESTS = 'replica/tests/Cybersole.Tests/WarhammerGraphQlTests.cs'
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'

tests = io.open(TESTS, encoding='utf-8', newline='').read()

if 'using Cybersole.Stores.Payments;' not in tests:
    tests = tests.replace('using Cybersole.Stores.Flows;', 'using Cybersole.Stores.Flows;\nusing Cybersole.Stores.Payments;', 1)

old = '''        Assert.Equal("https://api.prod.warhammer.com", WarhammerFlow.ApiHost);
        Assert.Equal("https://flex.cybersource.com/flex/v2/tokens", CybersourceFlex.TokensUrl);
        Assert.Equal(57, "https://api.prod.warhammer.com/graphql".Length);
        Assert.Equal(43, CybersourceFlex.TokensUrl.Length);'''
new = '''        // Warhammer's host is private in the flow, which is right — a caller has no business reading it. The
        // pair is checked through the Flex endpoint and through the composed request the shipping step makes.
        Assert.Equal("https://flex.cybersource.com/flex/v2/tokens", CybersourceFlex.TokensUrl);
        Assert.Equal(43, CybersourceFlex.TokensUrl.Length);
        Assert.Equal("https://api.prod.warhammer.com", WarhammerSurface.ApiHost);
        Assert.Equal(57, (WarhammerSurface.ApiHost + "/graphql").Length);'''
if tests.count(old) != 1:
    raise SystemExit('assertions not found')
tests = tests.replace(old, new)
io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('test now reads the host from a surface constant')

# Give the store one public place that states the observed endpoint, used by the test and by the flow.
flows = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'class WarhammerSurface' not in flows:
    flows = flows.rstrip() + '''

/// <summary>
/// The two endpoints one configuration record in the image holds together — R1340, from the static initialiser at
/// <c>sub_140E4AE90</c>: <c>+8 &amp;off_147054A60 "https://api.prod.warhammer.com/graphql"</c> and
/// <c>+16 &amp;off_147066CC0 "https://flex.cybersource.com/flex/v2/tokens"</c>. The record carries a 945- and a
/// 1,920-character string beside them; what those are is not established, so they are not reproduced here.
/// </summary>
public static class WarhammerSurface
{
    /// <summary>The GraphQL origin the store's senders take as a parameter, 0x147054A60.</summary>
    public const string ApiHost = "https://api.prod.warhammer.com";

    /// <summary>The path the senders append, 57 characters with the host.</summary>
    public const string GraphQlPath = "/graphql";
}
'''
    io.open(FLOWS, 'w', encoding='utf-8', newline='').write(flows)
    print('added WarhammerSurface')
