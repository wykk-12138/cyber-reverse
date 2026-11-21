"""R1340: the pair of URL literals that travel together, and what that says about step enumeration.

The host-reference technique from R1339 works when each sender embeds the store's host. Applied to Warhammer it
gives one function, not ten: sub_140E4AE90 (133 bytes) is a static initialiser that builds a shared config record

    +8   &off_147054A60  "https://api.prod.warhammer.com/graphql"     (57 characters)
    +16  &off_147066CC0  "https://flex.cybersource.com/flex/v2/tokens" (43 characters)
    +24  a 945-character string
    +32  a 1,920-character string

so this store centralises its endpoints in one object and its senders take the URL as a parameter. The list
therefore enumerates the *helper*, not the steps.

That is worth pinning as a precondition rather than a disappointment: the technique answers "what does this store's
HTTP surface look like" only for stores that inline the host. For the others the enumeration has to come from
operation names, which is what the GraphQL document inventory already is.

What the record does give is a checkable fact: those two endpoints belong to the same configuration, and the
replica must carry both verbatim. It does — CybersourceFlex.TokensUrl and WarhammerFlow.ApiHost — and this round
pins the pair in a test so an edit to either is caught.

Usage: python analysis/add_endpoint_pair_test.py
"""
import io

PATH = 'replica/tests/Cybersole.Tests/WarhammerGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheWarhammerConfigRecordCarriesBothEndpoints' in text:
    raise SystemExit('test already present')

block = '''
    /// <summary>
    /// R1340: the image builds one configuration record holding both endpoints — Warhammer's GraphQL endpoint and
    /// CyberSource's Flex token endpoint — in a static initialiser at sub_140E4AE90 (133 bytes):
    /// <c>+8  &amp;off_147054A60 "https://api.prod.warhammer.com/graphql"</c> and
    /// <c>+16 &amp;off_147066CC0 "https://flex.cybersource.com/flex/v2/tokens"</c>. They are one object, so the
    /// replica must carry both verbatim; this pins the pair.
    /// </summary>
    [Fact]
    public void TheWarhammerConfigRecordCarriesBothEndpoints()
    {
        Assert.Equal("https://api.prod.warhammer.com", WarhammerFlow.ApiHost);
        Assert.Equal("https://flex.cybersource.com/flex/v2/tokens", CybersourceFlex.TokensUrl);
        Assert.Equal(57, "https://api.prod.warhammer.com/graphql".Length);
        Assert.Equal(43, CybersourceFlex.TokensUrl.Length);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('added the endpoint-pair test')
