"""R1334 tests: the cartApi endpoint rule, and that a full URL passes through untouched."""

import io

PATH = 'replica/tests/Cybersole.Tests/MagentoCartTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'CartApiEndpointFor' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1334: the image composes the cart-API endpoint as "https://" + host-with-www-replaced-by-themeapis +
    /// "/cartApi/checkout" — sub_141CF82E0(host, "www", "themeapis") at 0x140C32471, with the literal
    /// https://themeapis. at 0x14708885C being what that yields for a host with no www prefix.
    /// </summary>
    [Theory]
    [InlineData("www.casio.com", "https://themeapis.casio.com/cartApi/checkout")]
    [InlineData("casio.com", "https://themeapis.casio.com/cartApi/checkout")]
    [InlineData("https://www.example.test/", "https://themeapis.example.test/cartApi/checkout")]
    [InlineData("shop.test", "https://themeapis.shop.test/cartApi/checkout")]
    public void TheCartApiEndpointReplacesWwwWithThemeapis(string input, string expected)
    {
        Assert.Equal(expected, MagentoCart.CartApiEndpointFor(input));
    }

    /// <summary>
    /// Every caller today hands in a full URL, and must keep getting exactly that: the composition is for a bare
    /// host, which is the case that previously produced a request to nowhere.
    /// </summary>
    [Fact]
    public void AFullUrlPassesThroughTheResolverUntouched()
    {
        Assert.Equal("https://shop.test/graphql", MagentoCart.ResolveEndpoint("https://shop.test/graphql"));
        Assert.Equal("https://themeapis.shop.test/cartApi/checkout", MagentoCart.ResolveEndpoint("shop.test"));
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended the endpoint tests')
