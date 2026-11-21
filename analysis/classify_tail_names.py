"""Which of the 34 store-tail names have a standalone string, and which exist only mangled?

R1366 showed that GetCartId, GetCartCsrf and GetCartItemId appear only as <Name>d__NN, so they cannot be followed to a
handler. That conclusion was drawn from three names; this checks all 34, because the three might have been the
unlucky ones. A name with a standalone string can be followed the way R1355 followed cartLineItemSet — and a name
without one needs a different route entirely.

Usage: python analysis/classify_tail_names.py
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

NAMES = [
    'AddAddress', 'ClearActiveCart', 'FetchProductProperties', 'FilterBrokerAccountsByEnvAsync',
    'FindAccountAsync', 'FindEarlyAccessProduct', 'FindHCaptchaInformationAsync', 'FindProductStoreFront',
    'GetActiveCart', 'GetCartCsrf', 'GetCartId', 'GetCartItemId', 'GetHomepagePreloadVariant', 'GetLogin',
    'GetProductHtml', 'GetProductZgwMobile', 'HandleCartUpdate', 'LoadProduct', 'ReplaceProduct',
    'ReserveProduct', 'SaveAddress', 'ScrapeCaptchaKey', 'ScrapeProductData',
    'ScrapeVariantAvailabilityStorefront', 'SearchProduct', 'SelectVariant', 'SendAsyncMultiProxy',
    'SetCachedProductAsync', 'SetupProxySession', 'SolveBotCaptcha',
]


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


standalone = []
mangled_only = []

for name in NAMES:
    listing = run('analysis/ida.py', 'str', name, '--limit', '10')
    try:
        matches = json.loads(listing).get('matches', [])
    except json.JSONDecodeError:
        mangled_only.append((name, 'listing unreadable'))
        continue

    exact = [m for m in matches if m.get('string') == name]
    if exact:
        standalone.append((name, exact[0]['addr']))
    else:
        sample = matches[0]['string'][:40] if matches else '(no match)'
        mangled_only.append((name, sample))

print('names checked: %d' % len(NAMES))
print()
print('standalone string (tractable by name -> handler): %d' % len(standalone))
for name, address in standalone:
    print('   %-34s %s' % (name, address))
print()
print('mangled only or absent: %d' % len(mangled_only))
for name, sample in mangled_only:
    print('   %-34s %s' % (name, sample))
