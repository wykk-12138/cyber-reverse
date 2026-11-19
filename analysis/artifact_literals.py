"""Probe the published NativeAOT artifact for literals, in both encodings a frozen string can take.

Why this exists: R1236 searched the artifact for ASCII bytes only and concluded that the entire payment layer had
been trimmed, because api.midtrans.com did not appear as ASCII. Re-running with UTF-16LE shows api.stripe.com,
api.unzer.com, app.midtrans.com and paypal.com/graphql all present. NativeAOT stores frozen System.String payloads as
UTF-16, while some tables keep ASCII, so an ASCII-only probe produces false negatives -- the same shape as the R816
rule about a source that looks complete but is a sample.

Usage:
    python analysis/artifact_literals.py <artifact> <literal> [more literals...]
"""
import io
import sys


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path, probes = argv[0], argv[1:]
    blob = io.open(path, 'rb').read()
    print('artifact: %s  %d bytes' % (path, len(blob)))
    print('%-36s %-8s %-8s' % ('literal', 'ascii', 'utf16'))
    for s in probes:
        # A frozen string may appear in either encoding, and some appear in both, so a negative needs both to miss.
        print('%-36s %-8s %-8s'
              % (s, s.encode('ascii', 'ignore') in blob, s.encode('utf-16-le') in blob))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
