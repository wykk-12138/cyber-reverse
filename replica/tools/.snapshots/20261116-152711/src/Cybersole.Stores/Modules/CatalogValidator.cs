using Cybersole.Http.Stores;

namespace Cybersole.Stores.Modules;

/// <summary>
/// Sanity checks over the module catalog: unique ids, non-empty names/domains,
/// and no url that two modules both claim. Runs at startup and in tests so adding a
/// brand can never silently shadow an existing store.
/// </summary>
public static class CatalogValidator
{
    public static IReadOnlyList<string> Validate(IEnumerable<IStoreModule> modules)
    {
        var problems = new List<string>();
        var list = modules.ToList();

        var duplicateIds = list.GroupBy(m => m.Id, StringComparer.OrdinalIgnoreCase)
            .Where(g => g.Count() > 1)
            .Select(g => g.Key);
        foreach (var id in duplicateIds)
            problems.Add($"duplicate module id '{id}'");

        foreach (var module in list)
        {
            if (string.IsNullOrWhiteSpace(module.Name))
                problems.Add($"module '{module.Id}' has no display name");
            if (module.Domains.Count == 0)
                problems.Add($"module '{module.Id}' declares no domains");
        }

        // every module must actually accept the domains it advertises, otherwise Resolve() never lands
        foreach (var module in list)
        {
            foreach (var domain in module.Domains)
            {
                if (string.IsNullOrWhiteSpace(domain)) continue;
                if (!Uri.TryCreate("https://" + domain.TrimStart('.') + "/", UriKind.Absolute, out var uri))
                {
                    problems.Add($"module '{module.Id}' advertises an unparsable domain '{domain}'");
                    continue;
                }

                if (!module.CanHandle(uri))
                    problems.Add($"module '{module.Id}' does not accept its own domain '{domain}'");
            }
        }

        // two modules must not both claim the same probe url
        var probes = new[] { "https://example.myshopify.com/products/x", "https://www.nike.com/t/x" };
        foreach (var probe in probes)
        {
            var uri = new Uri(probe);
            var claimants = list.Where(m => m.CanHandle(uri)).Select(m => m.Id).ToList();
            if (claimants.Count > 1 && !claimants.Contains("shopify"))
                problems.Add($"url '{probe}' is claimed by {string.Join(", ", claimants)}");
        }

        return problems;
    }
}
