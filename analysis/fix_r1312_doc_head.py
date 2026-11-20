"""R1312: fix the composed document head to match the bracket the captured tail demands.

The tail begins with `"]}}`. A `]` cannot close an object, so the filter carries a list — the head has to
open `sku:{in:[` and let the tail's quote close the value, its bracket close the list and its two braces
close sku and filter. The first version wrote `sku:{eq:"X"}}` and then appended a tail that starts with
another quote, which produced an unbalanced document and a GraphQL error the tests caught.

Also fixes SearchAsync's URL handling: a caller passing an absolute URL got it concatenated onto the
origin, producing `http://hosthttp://host/graphql`. TinyServer-based tests use absolute URLs, so this was
the difference between a working call and a null product.
"""
import io
import sys

PATH = 'replica/src/Cybersole.Stores/Flows/CasioGraphQL.cs'

text = io.open(PATH, encoding='utf-8').read()

old_head = (
    '        // The captured tail already carries the ",sort:...,pageSize:40){items{...}} total_count}}" that\n'
    '        // closes the call, so the head only has to open it and supply the filter.\n'
    '        return "query{products(filter:{sku:{eq:\\"" + escaped + "\\"}}" + ObservedSelection;'
)
new_head = (
    '        // The captured tail begins with the quote that closes the filter\'s value and the bracket that\n'
    '        // closes its list, so the head opens `sku:{in:[` and the tail completes it.\n'
    '        return "query{products(filter:{sku:{in:[\\"" + escaped + ObservedSelection;'
)

if text.count(old_head) != 1:
    print('head anchor: %d (want 1)' % text.count(old_head))
    sys.exit(1)
text = text.replace(old_head, new_head)

old_url = '        var url = Payments.GatewayHttp.OriginOf(c.Url) + (path ?? Path);'
new_url = (
    '        var target = path ?? Path;\n'
    '        // A caller may hand in an absolute endpoint (tests do); only a relative path gets the origin.\n'
    '        var url = target.StartsWith("http", StringComparison.OrdinalIgnoreCase)\n'
    '            ? target\n'
    '            : Payments.GatewayHttp.OriginOf(c.Url) + target;'
)
if text.count(old_url) != 1:
    print('url anchor: %d (want 1)' % text.count(old_url))
    sys.exit(1)
text = text.replace(old_url, new_url)

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('patched both')
