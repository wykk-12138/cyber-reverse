"""R1344: the checker that finds what R1331 could not see, and the one candidate it found that matters.

The gap R1343 exposed was that "the document has a caller" does not imply "the method that sends it has a caller".
This asks the next question directly: which public types does no other file refer to? Across the replica that is
183 of 643, and almost all of them are models — deserialized from JSON, bound from XAML, instantiated by the
framework rather than by a line of C#. The useful slice is Cybersole.Stores, and in it one entry stands out:
ShopAppProduct, the class last round added, referenced only by its own tests.

One honest complication: the artifact still contains its strings. `query ProductDetails` and `server.shop.app` are
both present as UTF-16 even though no production line names the type. So source-level "no caller" is weaker than
the R1343 differential — it is a candidate list, not a verdict, and it must not become a hard invariant. §4.5 is
about the artifact, and the artifact says this one survives.

What that leaves is a decision rather than a check: ShopAppProduct has no consumer in the replica's flow set, and
hoping for the best is not a design. It gets one — ShopifyFlow.FindProductAsync, which already looks a product up
by handle, takes the Shop app query when a run supplies the identifiers that query needs.

Usage: python analysis/wire_shop_app_product.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'ShopAppProduct' in text:
    raise SystemExit('already wired')

old = '''        var handle = ProductHandle(c.Url);
        if (handle is null) return StepOutcome.Fail("shopify: cannot resolve product handle from url");'''

new = '''        // R1344: the Shop app's product query, when the run carries the identifiers it needs. It is a different
        // API from this store's storefront — server.shop.app, not the store's /products/<handle>.js — so it is a
        // branch, not a replacement, and the branch only exists when the session supplies its variables.
        var brokerId = c.Session.Vars.GetValueOrDefault("shopapp.brokerId");
        if (!string.IsNullOrEmpty(brokerId))
        {
            var shopAppVariables = new JObject
            {
                ["brokerId"] = brokerId,
                ["productId"] = c.Session.Vars.GetValueOrDefault("shopapp.productId") ?? c.Session.ProductId,
                ["imageWidth"] = int.TryParse(c.Session.Vars.GetValueOrDefault("shopapp.imageWidth"), out var width)
                    ? width
                    : 800,
                ["variantsLimit"] = int.TryParse(c.Session.Vars.GetValueOrDefault("shopapp.variantsLimit"), out var limit)
                    ? limit
                    : 250,
                ["sortReviewsBy"] = ShopAppProduct.SortRecommended,
            };

            if (c.Session.Vars.TryGetValue("shopapp.productInput", out var productInput) &&
                !string.IsNullOrWhiteSpace(productInput))
            {
                try
                {
                    shopAppVariables["productInput"] = JObject.Parse(productInput);
                }
                catch (Newtonsoft.Json.JsonException)
                {
                    return StepOutcome.Fail("shopify: shopapp.productInput is not valid JSON");
                }
            }

            var (product, shopAppError) = await ShopAppProduct
                .FetchAsync(c, shopAppVariables, ct, c.Session.Vars.GetValueOrDefault("shopapp.url"))
                .ConfigureAwait(false);

            if (product is null) return StepOutcome.Fail(shopAppError);

            c.Session.Vars["product"] = product.ToString(Newtonsoft.Json.Formatting.None);
            var productId = product["id"]?.ToString();
            if (!string.IsNullOrEmpty(productId)) c.Session.ProductId = productId;
            return StepOutcome.Success();
        }

        var handle = ProductHandle(c.Url);
        if (handle is null) return StepOutcome.Fail("shopify: cannot resolve product handle from url");'''

if text.count(old) != 1:
    raise SystemExit('anchor found %d times' % text.count(old))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('wired ShopAppProduct into ShopifyFlow.FindProductAsync')
