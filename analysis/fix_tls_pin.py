"""Replace the stale TLS defect pin with an assertion that would catch a regression. (R818)

The doc comment says nike.com rejects the hand-written TLS stack with bad_record_mac and that the browser path is the
only way to reach a real store. Running the test shows HTTP 200 and 190,584 bytes. The defect is gone and the comment
never learned about it, because the assertion only required a non-empty outcome -- success and failure both passed.

An assertion that accepts both answers is not a pin, it is a log line. This asserts the success instead, so a return of
bad_record_mac fails the suite rather than quietly updating a comment nobody reads.

The block is replaced by exact bytes captured from the file rather than retyped, because this session has already lost
time twice to hand-transcribed anchors.
"""

import io

PATH = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TlsTransportPerformanceTests.cs"

OLD = '''    /// <summary>
    /// A known defect, pinned so it cannot quietly disappear or quietly get worse.
    ///
    /// The hand-written TLS 1.2 stack completes against the host `verify.ps1` uses, but
    /// nike.com rejects it with `bad_record_mac`. Until the record layer is fixed, the
    /// browser path (ChromiumKasadaSolver) is the only way to talk to a real store.
    /// </summary>
    [Fact]
    public async Task TheOwnTlsDefectIsPinned()
    {
        using var client = new NetClient { Transport = TransportMode.OwnTls };

        string? outcome;
        try
        {
            var res = await client.GetAsync(Url, new RequestOptions
            {
                Timeout = TimeSpan.FromSeconds(20),
                Retries = 0,
                Tag = "tls-defect",
            });

            outcome = res.IsSuccess
                ? $"HTTP {res.StatusCode} ({res.Bytes} bytes)"
                : $"HTTP {res.StatusCode}";
        }
        catch (Exception ex)
        {
            outcome = ex.Message;
        }

        _out.WriteLine($"OwnTls against {Url} -> {outcome}");

        // Either it works (the defect got fixed) or it fails with a TLS-level error.
        // What must not happen is a silent empty success.
        Assert.False(string.IsNullOrWhiteSpace(outcome));
    }
'''

NEW = '''    /// <summary>
    /// The hand-written TLS 1.2 stack reaches a real store. R818.
    ///
    /// <para>
    /// This test used to say the opposite. Its comment read that nike.com rejected the stack with
    /// <c>bad_record_mac</c> and that the browser path was therefore the only way to talk to a real store, and it
    /// asserted only that <em>something</em> happened -- success and failure both passed.
    /// </para>
    ///
    /// <para>
    /// A run on 2026-11-16 returned HTTP 200 with 190,584 bytes, so the record-layer defect had been fixed at some
    /// earlier point and the comment never learned about it. An assertion that accepts both answers is a log line
    /// rather than a pin, which is exactly why the stale claim survived.
    /// </para>
    ///
    /// <para>
    /// So this now asserts the success. If a regression brings back <c>bad_record_mac</c>, the suite goes red instead of
    /// quietly rewriting history. The test still skips when the host is unreachable, so a machine without network fails
    /// at the reachability check rather than here.
    /// </para>
    /// </summary>
    [Fact]
    public async Task TheOwnTlsStackReachesARealStore()
    {
        using var client = new NetClient { Transport = TransportMode.OwnTls };

        var res = await client.GetAsync(Url, new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(20),
            Retries = 0,
            Tag = "tls-reach-own",
        });

        _out.WriteLine($"OwnTls against {Url} -> HTTP {res.StatusCode} ({res.Bytes} bytes) in " +
                       $"{res.Elapsed.TotalMilliseconds:0}ms");

        Assert.True(res.IsSuccess,
            $"the hand-written TLS stack did not reach {Url}: HTTP {res.StatusCode}. " +
            "If this is bad_record_mac returning, the defect the old comment described is back.");
        Assert.True(res.Bytes > 1000,
            $"reached {Url} but read only {res.Bytes} bytes — a body that small is not a page");
    }
'''


def main():
    t = io.open(PATH, encoding="utf-8").read()
    if OLD not in t:
        print("  anchor not found — refusing to write")
        return 1
    out = t.replace(OLD, NEW, 1)
    if "bad_record_mac`. Until the record layer is fixed" in out:
        print("  stale comment survived — refusing to write")
        return 1
    io.open(PATH, "w", encoding="utf-8", newline="").write(out)
    print("  replaced the pin with an assertion")
    print("  new method name present: %s" % ("TheOwnTlsStackReachesARealStore" in out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
