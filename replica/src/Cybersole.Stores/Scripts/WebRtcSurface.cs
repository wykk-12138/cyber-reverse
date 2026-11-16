namespace Cybersole.Stores.Scripts;

/// <summary>
/// <c>RTCPeerConnection</c>: the surface that leaks an address the rest of the persona does not claim.
///
/// <para>
/// Every other surface in this directory makes the browser <i>report</i> something consistent — canvas pixels, WebGL
/// strings, font metrics, media queries. This one is different in kind: WebRTC does not report a value, it opens
/// channels that answer with network addresses. A page can build an offer, gather ICE candidates, and read from them
/// the machine's private address and, without a relay-forcing policy, its public one. Under a proxy those are the
/// addresses the proxy exists to hide.
/// </para>
///
/// <para>
/// So the posture is not "report a persona" but "report nothing the persona did not claim". Two leaks matter:
/// </para>
///
/// <code>
/// mDNS candidates  -- Chromium obfuscates host candidates as a .local name; still an identifier, still stable
///                    per machine, so it correlates sessions even though it names no address
/// srflx candidates -- gathered by asking a STUN server what the source address appears to be; under a proxy this
///                    is the proxy's address, without one it is the real public address
/// </code>
///
/// <para>
/// <b>Why this is absent until now.</b> The replica's flows are a TLS client, not a browser, and a TLS client has no
/// WebRTC to leak from. This surface exists for the solver path, where a real Chromium runs behind a proxy and the
/// page may legitimately ask. The image names <c>SubmitWebRtc</c> among its submit steps, which is what put this on
/// the list; the four sibling surfaces — canvas, WebGL, font, media — were already here and this one was not.
/// </para>
///
/// <para>
/// <b>What is inference.</b> The exact policy the original applies. What is observed is that a step named
/// <c>SubmitWebRtc</c> exists; whether it blocks, spoofs, or merely records is not established by the name. This
/// implements the guard that a proxied browser needs — suppress srflx and host candidates, keep the connection
/// constructible — and states the choice rather than presenting it as the original's.
/// </para>
/// </summary>
public static class WebRtcSurface
{
    /// <summary>The rule, in one line, for a caller deciding whether to install this.</summary>
    public const string Rule =
        "a proxied browser must not let WebRTC report an address the proxy hides; that is not a value to spoof";

    /// <summary>
    /// The two candidate kinds and what each gives away. Named separately because a caller may want one and not the
    /// other: suppressing srflx is always right under a proxy, while suppressing host candidates is a judgement.
    /// </summary>
    public const string CandidateLeaks =
        "host candidates name the private address or an mDNS name stable per machine; srflx candidates name the public address";

    /// <summary>
    /// The JavaScript that installs the guard.
    ///
    /// <para>
    /// It wraps <c>RTCPeerConnection</c> so that <c>onicecandidate</c> never sees srflx or host candidates, and so that
    /// <c>localDescription</c> has its candidates stripped to match. Both halves are needed: a page that reads
    /// <c>localDescription.sdp</c> directly would otherwise still see what the event handler suppressed.
    /// </para>
    /// </summary>
    public static string BodyJs() => """
        // ---- RTCPeerConnection (R914) ---------------------------------------------------------
        //
        // Suppress srflx and host ICE candidates while keeping the connection usable. Both the event and the SDP
        // have to agree: wrapping onicecandidate alone leaves localDescription.sdp carrying the same candidates.

        (() => {
          const PC = window.RTCPeerConnection;
          if (!PC) return;

          const BLOCKED = / typ (srflx|host) /;

          function stripSdp(sdp) {
            if (typeof sdp !== "string") return sdp;
            return sdp
              .split("\r\n")
              .filter((line) => !(line.startsWith("a=candidate:") && BLOCKED.test(line + " ")))
              .join("\r\n");
          }

          function wrap(pc) {
            const desc = Object.getOwnPropertyDescriptor(PC.prototype, "localDescription");
            if (desc && desc.get) {
              Object.defineProperty(pc, "localDescription", {
                configurable: true,
                get() {
                  const d = desc.get.call(pc);
                  return d && d.sdp ? { type: d.type, sdp: stripSdp(d.sdp) } : d;
                },
              });
            }

            const add = pc.addEventListener.bind(pc);
            pc.addEventListener = function (type, listener, opts) {
              if (type !== "icecandidate" || typeof listener !== "function") {
                return add(type, listener, opts);
              }
              return add(type, function (ev) {
                const c = ev && ev.candidate;
                if (c && typeof c.candidate === "string" && BLOCKED.test(c.candidate + " ")) return;
                return listener.call(this, ev);
              }, opts);
            };
            return pc;
          }

          const Wrapped = function (...args) {
            return wrap(new PC(...args));
          };
          Wrapped.prototype = PC.prototype;
          Object.setPrototypeOf(Wrapped, PC);
          window.RTCPeerConnection = Wrapped;
        })();
        """;

    /// <summary>
    /// True when this surface must be installed for a session to be coherent: a session carrying a proxy has an
    /// address to protect. Exposed as data so a caller cannot forget the condition.
    /// </summary>
    public static bool RequiredFor(bool behindProxy) => behindProxy;
}