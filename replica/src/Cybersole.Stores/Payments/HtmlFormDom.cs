using AngleSharp.Dom;
using AngleSharp.Html.Dom;
using AngleSharp.Html.Parser;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Parsed HTML form metadata and default control values recovered via AngleSharp HTML5 DOM parsing.
/// </summary>
public sealed record HtmlForm(
    string? Id,
    string? Name,
    string? Action,
    string Method,
    Dictionary<string, string> Inputs);

/// <summary>
/// AOT-safe HTML5 DOM helpers powered by <see cref="HtmlParser"/> for form extraction,
/// selector queries, metadata lookup, and title/text extraction.
/// </summary>
public static class HtmlFormDom
{
    private static IHtmlDocument? ParseDocument(string? html)
    {
        if (string.IsNullOrWhiteSpace(html))
            return null;
        return new HtmlParser().ParseDocument(html!);
    }

    /// <summary>
    /// Parse a single matching form (by <paramref name="formId"/> and/or <paramref name="formName"/>,
    /// or the first <c>&lt;form&gt;</c> when neither is supplied) into <c>(Action, Inputs)</c>.
    /// </summary>
    public static (string Action, Dictionary<string, string> Inputs) ExtractForm(
        string? html, string? formName = null, string? formId = null)
    {
        var form = ExtractFormInfo(html, formName, formId);
        return form is null
            ? (string.Empty, new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase))
            : (form.Action ?? string.Empty, form.Inputs);
    }

    /// <summary>
    /// Parse a matching <c>&lt;form&gt;</c> into a full <see cref="HtmlForm"/> descriptor,
    /// returning <see langword="null"/> when no matching <c>&lt;form&gt;</c> exists.
    /// </summary>
    public static HtmlForm? ExtractFormInfo(
        string? html,
        string? formName = null,
        string? formId = null,
        bool matchAnyIdOrName = false)
    {
        var doc = ParseDocument(html);
        if (doc is null) return null;

        IHtmlFormElement? target = null;
        foreach (var form in doc.Forms)
        {
            if (matchAnyIdOrName)
            {
                var idHit = !string.IsNullOrEmpty(formId) &&
                            string.Equals(form.Id, formId, StringComparison.OrdinalIgnoreCase);
                var nameHit = !string.IsNullOrEmpty(formName) &&
                              string.Equals(form.Name, formName, StringComparison.OrdinalIgnoreCase);
                if (idHit || nameHit)
                {
                    target = form;
                    break;
                }
            }
            else
            {
                if (!string.IsNullOrEmpty(formId) &&
                    !string.Equals(form.Id, formId, StringComparison.OrdinalIgnoreCase))
                    continue;
                if (!string.IsNullOrEmpty(formName) &&
                    !string.Equals(form.Name, formName, StringComparison.OrdinalIgnoreCase))
                    continue;
                target = form;
                break;
            }
        }

        return target is null ? null : BuildForm(target);
    }

    /// <summary>
    /// Parse the first <c>&lt;form&gt;</c> matching <paramref name="cssSelector"/>.
    /// </summary>
    public static HtmlForm? ExtractFormBySelector(string? html, string cssSelector)
    {
        if (string.IsNullOrWhiteSpace(cssSelector))
            return null;
        var doc = ParseDocument(html);
        if (doc is null) return null;

        try
        {
            return doc.QuerySelector(cssSelector) is IHtmlFormElement form ? BuildForm(form) : null;
        }
        catch (DomException)
        {
            return null;
        }
    }

    /// <summary>Extract every <c>&lt;form&gt;</c> in document order.</summary>
    public static IReadOnlyList<HtmlForm> ExtractAllForms(string? html)
    {
        var doc = ParseDocument(html);
        if (doc is null || doc.Forms.Length == 0)
            return Array.Empty<HtmlForm>();

        var result = new List<HtmlForm>(doc.Forms.Length);
        foreach (var form in doc.Forms)
            result.Add(BuildForm(form));
        return result;
    }

    /// <summary>
    /// Collect all submittable named controls (<c>input</c>, <c>select</c>, <c>textarea</c>,
    /// submit <c>button</c>) across the HTML document using ordinal-ignore-case keys.
    /// </summary>
    public static Dictionary<string, string> ExtractInputs(string? html)
    {
        var doc = ParseDocument(html);
        return doc?.DocumentElement is null
            ? new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            : CollectControls(doc.DocumentElement);
    }

    /// <summary>Extract the trimmed HTML <c>&lt;title&gt;</c> text, or <see langword="null"/> if absent.</summary>
    public static string? ExtractTitle(string? html)
    {
        var doc = ParseDocument(html);
        if (doc is null) return null;
        var titleEl = doc.QuerySelector("title");
        return titleEl is null ? null : (titleEl.TextContent ?? string.Empty).Trim();
    }

    /// <summary>Return true when at least one element matches <paramref name="cssSelector"/>.</summary>
    public static bool HasElement(string? html, string cssSelector)
    {
        if (string.IsNullOrWhiteSpace(cssSelector)) return false;
        var doc = ParseDocument(html);
        if (doc is null) return false;
        try
        {
            return doc.QuerySelector(cssSelector) is not null;
        }
        catch (DomException)
        {
            return false;
        }
    }

    /// <summary>Return the trimmed text content of the first element matching <paramref name="cssSelector"/>.</summary>
    public static string? ExtractElementText(string? html, string cssSelector)
    {
        if (string.IsNullOrWhiteSpace(cssSelector)) return null;
        var doc = ParseDocument(html);
        if (doc is null) return null;

        try
        {
            var el = doc.QuerySelector(cssSelector);
            return el is null ? null : (el.TextContent ?? string.Empty).Trim();
        }
        catch (DomException)
        {
            return null;
        }
    }

    /// <summary>Return the value of <paramref name="attribute"/> on the first element matching <paramref name="cssSelector"/>.</summary>
    public static string? ExtractElementAttribute(string? html, string cssSelector, string attribute)
    {
        if (string.IsNullOrWhiteSpace(cssSelector) || string.IsNullOrWhiteSpace(attribute))
            return null;
        var doc = ParseDocument(html);
        if (doc is null) return null;

        try
        {
            return doc.QuerySelector(cssSelector)?.GetAttribute(attribute);
        }
        catch (DomException)
        {
            return null;
        }
    }

    /// <summary>
    /// Lookup an element by exact <paramref name="id"/> (supporting colons/leading digits that are invalid
    /// in unescaped CSS ID selectors) and read <paramref name="attribute"/>.
    /// </summary>
    public static string? ExtractElementAttributeById(string? html, string id, string attribute)
    {
        if (string.IsNullOrEmpty(id) || string.IsNullOrWhiteSpace(attribute))
            return null;
        var doc = ParseDocument(html);
        return doc?.GetElementById(id)?.GetAttribute(attribute);
    }

    /// <summary>
    /// Lookup an element by exact <paramref name="id"/> and return all of its attributes (case-insensitive).
    /// </summary>
    public static Dictionary<string, string>? ExtractElementAttributesById(string? html, string id)
    {
        if (string.IsNullOrEmpty(id)) return null;
        var doc = ParseDocument(html);
        var el = doc?.GetElementById(id);
        if (el is null) return null;

        var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var attr in el.Attributes)
            dict[attr.Name] = attr.Value;
        return dict;
    }

    /// <summary>Read <c>&lt;meta name="..." content="..."&gt;</c> case-insensitively.</summary>
    public static string? ExtractMetaContent(string? html, string metaName)
    {
        if (string.IsNullOrEmpty(metaName)) return null;
        var doc = ParseDocument(html);
        if (doc is null) return null;

        foreach (var meta in doc.QuerySelectorAll("meta"))
        {
            if (string.Equals(meta.GetAttribute("name"), metaName, StringComparison.OrdinalIgnoreCase))
            {
                var content = meta.GetAttribute("content");
                if (content is not null)
                    return content;
            }
        }
        return null;
    }

    private static HtmlForm BuildForm(IHtmlFormElement form)
    {
        var id = string.IsNullOrEmpty(form.Id) ? form.GetAttribute("id") : form.Id;
        var name = string.IsNullOrEmpty(form.Name) ? form.GetAttribute("name") : form.Name;
        var action = form.GetAttribute("action");
        var rawMethod = form.GetAttribute("method");
        var method = string.IsNullOrWhiteSpace(rawMethod) ? "GET" : rawMethod.Trim().ToUpperInvariant();
        return new HtmlForm(id, name, action, method, CollectControls(form));
    }

    private static Dictionary<string, string> CollectControls(IElement root)
    {
        var inputs = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var el in root.QuerySelectorAll("input, select, textarea, button"))
        {
            if (IsDisabled(el))
                continue;

            switch (el)
            {
                case IHtmlInputElement input:
                    AddInputControl(inputs, input);
                    break;
                case IHtmlSelectElement select:
                    AddSelectControl(inputs, select);
                    break;
                case IHtmlTextAreaElement textArea:
                    AddTextAreaControl(inputs, textArea);
                    break;
                case IHtmlButtonElement button:
                    AddButtonControl(inputs, button);
                    break;
            }
        }
        return inputs;
    }

    private static bool IsDisabled(IElement el)
    {
        if (el.HasAttribute("disabled"))
            return true;

        var fieldset = el.Closest("fieldset[disabled]");
        if (fieldset is not null)
        {
            var firstLegend = fieldset.QuerySelector("legend");
            if (firstLegend is null || !firstLegend.Contains(el))
                return true;
        }
        return false;
    }

    private static void AddInputControl(Dictionary<string, string> inputs, IHtmlInputElement input)
    {
        var name = input.Name;
        if (string.IsNullOrEmpty(name))
            return;

        var type = (input.GetAttribute("type") ?? "text").Trim().ToLowerInvariant();
        if (type is "button" or "reset" or "image" or "file")
            return;

        if (type is "checkbox" or "radio")
        {
            if (!input.IsChecked && !input.HasAttribute("checked"))
                return;
            inputs[name] = input.GetAttribute("value") ?? "on";
            return;
        }

        inputs[name] = input.GetAttribute("value") ?? string.Empty;
    }

    private static void AddSelectControl(Dictionary<string, string> inputs, IHtmlSelectElement select)
    {
        var name = select.Name;
        if (string.IsNullOrEmpty(name))
            return;

        IHtmlOptionElement? selected = null;
        IHtmlOptionElement? firstEnabled = null;
        foreach (var opt in select.Options)
        {
            if (opt.IsDisabled) continue;
            firstEnabled ??= opt;
            if (opt.IsSelected || opt.HasAttribute("selected"))
            {
                selected = opt;
                break;
            }
        }

        var chosen = selected ?? firstEnabled;
        if (chosen is not null)
            inputs[name] = chosen.Value;
    }

    private static void AddTextAreaControl(Dictionary<string, string> inputs, IHtmlTextAreaElement textArea)
    {
        var name = textArea.Name;
        if (string.IsNullOrEmpty(name))
            return;
        inputs[name] = textArea.Value ?? string.Empty;
    }

    private static void AddButtonControl(Dictionary<string, string> inputs, IHtmlButtonElement button)
    {
        var name = button.Name;
        if (string.IsNullOrEmpty(name))
            return;

        var type = (button.GetAttribute("type") ?? "submit").Trim().ToLowerInvariant();
        if (type is not ("submit" or ""))
            return;

        inputs[name] = button.GetAttribute("value") ?? button.TextContent;
    }
}
