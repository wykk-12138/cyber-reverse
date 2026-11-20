"""R1314: replace the inferred GraphQL wrapper with the one the image actually concatenates.

R1312 built the document from a tail plus a guessed head, and sent it as a POST body `{"query": ...}`.
Following a Casio-exclusive anchor instead of a generic one — `casio_image_url`, which has exactly one code
reference — lands on sub_14095A090, whose MoveNext does this:

    sub_141CF62D0(&off_147197250, *(v1 + 208), &off_146A758C0)   // string concat: head + sku + tail
    sub_141CF62D0(v5, &off_146B28A80, v6)                        // ... + "?query=" + that

and the two literals decode to

    0x147197250  len=28  '{products(filter:{sku:{in:["'
    0x146B28A80  len=7   '?query='

So the head is observed after all, the document is a shorthand query with no `query{...}` wrapper, and it
travels as a GET query parameter rather than in a POST body. The bracket reasoning in R1312 was right — the
tail's `"]` did mean `in:[` — and the transport was wrong.

This script rewrites the constants and the call so the source says what the image does.
"""
import io
import sys

PATH = 'replica/src/Cybersole.Stores/Flows/CasioGraphQL.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()


def replace_once(old, new, label):
    global text
    if text.count(old) != 1:
        print('%s anchor: %d (want 1)' % (label, text.count(old)))
        sys.exit(1)
    text = text.replace(old, new)
    print('patched %s' % label)


# 1) The head and the query parameter become observed constants.
replace_once(
    '    /// <summary>The sort the document asks for.</summary>\n'
    '    public const string Sort = "{name:ASC}";',
    '    /// <summary>The sort the document asks for.</summary>\n'
    '    public const string Sort = "{name:ASC}";\n'
    '\n'
    '    /// <summary>\n'
    '    /// The document\'s head, byte for byte from 0x147197250 (28 characters). R1313\'s note said the head had\n'
    '    /// not been recovered and had to be inferred; it had, and the inference was right — this is the string\n'
    '    /// that opens <c>sku:{in:[</c>, which is why the captured tail could begin with <c>"]</c>.\n'
    '    /// </summary>\n'
    '    public const string ObservedHead = "{products(filter:{sku:{in:[\\"";\n'
    '\n'
    '    /// <summary>\n'
    '    /// The query parameter the document travels in, from 0x146B28A80 (7 characters). The image concatenates\n'
    '    /// it after the endpoint, so the search is a <b>GET</b> — a POST with a JSON body would be a different\n'
    '    /// request from the one this store is built for.\n'
    '    /// </summary>\n'
    '    public const string QueryParameter = "?query=";',
    'head and query parameter')

# 2) The document is head + sku + tail, with no wrapper of its own.
old_doc_start = text.index('    /// <summary>\n    /// The document, wrapped around the observed selection.')
old_doc_end = text.index('    /// <summary>The request body: a GraphQL POST with the document under <c>query</c>.</summary>')
new_doc = (
    '    /// <summary>\n'
    '    /// The document as the image builds it: the head, the sku, the tail — concatenated, with no <c>query{...}</c>\n'
    '    /// wrapper, because a Magento shorthand query is the braces themselves.\n'
    '    /// </summary>\n'
    '    public static string SearchDocument(string skuOrName)\n'
    '    {\n'
    '        var escaped = (skuOrName ?? string.Empty)\n'
    '            .Replace("\\\\", "\\\\\\\\", StringComparison.Ordinal)\n'
    '            .Replace("\\"", "\\\\\\"", StringComparison.Ordinal);\n'
    '\n'
    '        return ObservedHead + escaped + ObservedSelection;\n'
    '    }\n'
    '\n'
    '    /// <summary>The URL for a search: the endpoint, the query parameter and the encoded document.</summary>\n'
    '    public static string SearchUrl(string origin, string skuOrName) =>\n'
    '        origin.TrimEnd(\'/\') + Path + QueryParameter + Uri.EscapeDataString(SearchDocument(skuOrName));\n'
    '\n'
)
text = text[:old_doc_start] + new_doc + text[old_doc_end:]
print('patched document builder')

# 3) The body helper becomes a URL helper.
replace_once(
    '    /// <summary>The request body: a GraphQL POST with the document under <c>query</c>.</summary>\n'
    '    public static JObject SearchBody(string skuOrName) =>\n'
    '        new() { ["query"] = SearchDocument(skuOrName) };',
    '    /// <summary>Whether a URL is a GraphQL GET for this store — used by the caller to log what it sent.</summary>\n'
    '    public static bool IsSearchUrl(string url) =>\n'
    '        url.Contains(Path + QueryParameter, StringComparison.OrdinalIgnoreCase);',
    'body helper')

# 4) The call becomes a GET.
replace_once(
    '        var target = path ?? Path;\n'
    '        // A caller may hand in an absolute endpoint (tests do); only a relative path gets the origin.\n'
    '        var url = target.StartsWith("http", StringComparison.OrdinalIgnoreCase)\n'
    '            ? target\n'
    '            : Payments.GatewayHttp.OriginOf(c.Url) + target;\n'
    '        var body = document is null ? SearchBody(skuOrName) : new JObject { ["query"] = document };\n'
    '\n'
    '        var reply = await Payments.GatewayHttp\n'
    '            .PostAsync(c, url, body, "casio-graphql", ct)\n'
    '            .ConfigureAwait(false);\n'
    '\n'
    '        return ReadProduct(reply);',
    '        var target = path ?? Path;\n'
    '        // A caller may hand in an absolute endpoint (tests do); only a relative path gets the origin.\n'
    '        var origin = target.StartsWith("http", StringComparison.OrdinalIgnoreCase)\n'
    '            ? target.TrimEnd(\'/\')\n'
    '            : Payments.GatewayHttp.OriginOf(c.Url) + target.TrimEnd(\'/\');\n'
    '        var url = SearchUrl(origin, skuOrName);\n'
    '\n'
    '        JObject? reply;\n'
    '        try\n'
    '        {\n'
    '            var res = await c.Http.GetAsync(url, c.Options("casio-graphql"), ct).ConfigureAwait(false);\n'
    '            c.Session.AbsorbCookies(res.Cookies);\n'
    '            reply = res.IsSuccess ? JObject.Parse(res.Body) : null;\n'
    '        }\n'
    '        catch (Exception)\n'
    '        {\n'
    '            reply = null;\n'
    '        }\n'
    '\n'
    '        return ReadProduct(reply);',
    'search call')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('rewrote %s' % PATH)
