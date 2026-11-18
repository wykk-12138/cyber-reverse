using System.Security.Cryptography;
using System.Text;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// A minimal, deterministic browser environment for executing a vendor's anti-bot script
/// locally. The shipped Cybersole binary carries Jint 4.17.0 + Acornima 1.7.0 for exactly
/// this purpose: it runs the store's own JS instead of routing through a third-party solver.
/// </summary>
public sealed class BrowserShim
{
    public string UserAgent { get; init; } =
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
        "Chrome/131.0.0.0 Safari/537.36";

    public string Platform { get; init; } = "Win32";
    public string Language { get; init; } = "en-US";
    public int ScreenWidth { get; init; } = 1920;
    public int ScreenHeight { get; init; } = 1080;
    public int HardwareConcurrency { get; init; } = 8;
    public bool Headless { get; init; }

    public string Href { get; init; } = "about:blank";
    public string Cookie { get; set; } = string.Empty;
    public string Referrer { get; set; } = string.Empty;

    /// <summary>Values the script writes back into document.cookie.</summary>
    public List<string> WrittenCookies { get; } = new();

    public string BuildPrelude()
    {
        var lang = Language;
        var langBase = Language.Split('-')[0];
        var ua = UserAgent;
        var platform = Platform;
        var w = ScreenWidth;
        var h = ScreenHeight;
        var cores = HardwareConcurrency;
        var webdriver = Headless ? "true" : "false";
        var href = Href;
        var cookieTokens = string.Join(", ", Cookie
            .Split(';', StringSplitOptions.RemoveEmptyEntries)
            .Select(t => JsStr(t.Trim())));
        var referrer = Referrer;

        return $$"""
        var window = this;
        var self = this;
        var top = this;
        var parent = this;
        var frames = this;
        var __dshCookieStore = [{{cookieTokens}}];
        var document = {
          referrer: {{JsStr(referrer)}},
          title: "",
          readyState: "complete",
          hidden: false,
          visibilityState: "visible",
          characterSet: "UTF-8",
          contentType: "text/html",
          compatMode: "CSS1Compat",
          documentElement: { clientWidth: {{w}}, clientHeight: {{h}}, style: {} },
          body: { clientWidth: {{w}}, clientHeight: {{h}}, style: {}, appendChild: function (x) { return x; }, removeChild: function (x) { return x; } },
          head: { appendChild: function (x) { return x; }, removeChild: function (x) { return x; } },
          location: null,
          createElement: function (t) {
            return {
              tagName: String(t).toUpperCase(), style: {}, children: [], attributes: {}, dataset: {},
              appendChild: function (x) { this.children.push(x); return x; },
              removeChild: function (x) { return x; },
              setAttribute: function (k, v) { this.attributes[k] = v; },
              getAttribute: function (k) { return this.attributes[k] === undefined ? null : this.attributes[k]; },
              addEventListener: function () {}, removeEventListener: function () {},
              getContext: function () { return null; },
              parentNode: null, firstChild: null, nextSibling: null
            };
          },
          getElementById: function () { return null; },
          getElementsByTagName: function () { return []; },
          getElementsByClassName: function () { return []; },
          querySelector: function () { return null; },
          querySelectorAll: function () { return []; },
          addEventListener: function () {}, removeEventListener: function () {},
          hasFocus: function () { return true; }
        };
        var location = {
          href: {{JsStr(href)}}, protocol: "https:", host: "", hostname: "", port: "",
          pathname: "/", search: "", hash: "", origin: "",
          assign: function () {}, replace: function () {}, reload: function () {},
          toString: function () { return this.href; }
        };
        document.location = location;
        this.location = location;
        var navigator = {
          userAgent: {{JsStr(ua)}}, appVersion: {{JsStr(ua.Replace("Mozilla/", ""))}},
          appName: "Netscape", appCodeName: "Mozilla", product: "Gecko",
          platform: {{JsStr(platform)}}, vendor: "Google Inc.",
          language: {{JsStr(lang)}}, languages: [{{JsStr(lang)}}, {{JsStr(langBase)}}],
          onLine: true, cookieEnabled: true, doNotTrack: null,
          hardwareConcurrency: {{cores}}, deviceMemory: 8, maxTouchPoints: 0,
          webdriver: {{webdriver}},
          plugins: { length: 5, item: function () { return null; }, namedItem: function () { return null; } },
          mimeTypes: { length: 2 },
          sendBeacon: function () { return true; },
          javaEnabled: function () { return false; },
          getBattery: undefined
        };
        this.navigator = navigator;
        var screen = {
          width: {{w}}, height: {{h}}, availWidth: {{w}}, availHeight: {{h}},
          colorDepth: 24, pixelDepth: 24, orientation: { type: "landscape-primary", angle: 0 }
        };
        this.screen = screen;
        this.innerWidth = {{w}}; this.innerHeight = {{h}} - 120;
        this.outerWidth = {{w}}; this.outerHeight = {{h}};
        this.devicePixelRatio = 1;
        this.pageXOffset = 0; this.pageYOffset = 0;
        this.scrollX = 0; this.scrollY = 0;
        this.name = "";
        this.closed = false;
        this.length = 0;
        this.performance = {
          now: function () { return __dshNow(); },
          timeOrigin: 0,
          timing: { navigationStart: 0, domLoading: 1, loadEventEnd: 2 },
          getEntriesByType: function () { return []; },
          getEntriesByName: function () { return []; },
          mark: function () {}, measure: function () {}
        };
        this.crypto = {
          getRandomValues: function (arr) {
            var bytes = __dshRandom(arr.length);
            for (var i = 0; i < arr.length; i++) { arr[i] = bytes[i]; }
            return arr;
          },
          randomUUID: function () { return __dshUuid(); },
          /* A browser only exposes `subtle` in a secure context, which is why a naive shim leaves it
             undefined and why the payload's own literal table carries "sha256". Answered with the
             host's real hash: a stubbed digest would put a wrong value inside the token instead of
             failing where it can be seen. */
          subtle: {
            digest: function (alg, data) {
              try { return Promise.resolve(new Uint8Array(__dshDigest(__dshAlgName(alg), __dshBytes(data))).buffer); }
              catch (e) { return Promise.reject(e); }
            },
            importKey: function (fmt, keyData, alg, extractable, usages) {
              try {
                return Promise.resolve({ __dshKey: __dshBytes(keyData), algorithm: alg || {},
                                         type: "secret", extractable: !!extractable, usages: usages || [] });
              } catch (e) { return Promise.reject(e); }
            },
            sign: function (alg, key, data) {
              try {
                var name = alg && alg.hash ? alg.hash.name : alg;
                return Promise.resolve(new Uint8Array(__dshHmac(__dshAlgName(name), (key && key.__dshKey) || [], __dshBytes(data))).buffer);
              } catch (e) { return Promise.reject(e); }
            },
            verify: function () { return Promise.resolve(false); },
            generateKey: function () { return Promise.reject(new Error("subtle.generateKey is not available")); },
            exportKey: function () { return Promise.reject(new Error("subtle.exportKey is not available")); },
            encrypt: function () { return Promise.reject(new Error("subtle.encrypt is not available")); },
            decrypt: function () { return Promise.reject(new Error("subtle.decrypt is not available")); },
            deriveBits: function () { return Promise.reject(new Error("subtle.deriveBits is not available")); },
            deriveKey: function () { return Promise.reject(new Error("subtle.deriveKey is not available")); },
            wrapKey: function () { return Promise.reject(new Error("subtle.wrapKey is not available")); },
            unwrapKey: function () { return Promise.reject(new Error("subtle.unwrapKey is not available")); }
          }
        };
        function __dshBytes(data) {
          if (data === undefined || data === null) return [];
          var view = (data.length !== undefined) ? data : new Uint8Array(data);
          var out = [];
          for (var i = 0; i < view.length; i++) out.push(view[i] & 255);
          return out;
        }
        function __dshAlgName(alg) {
          var s = String(alg || "SHA-256").replace(/[^A-Za-z0-9]/g, "").toUpperCase();
          if (s === "SHA1" || s === "SHA256" || s === "SHA384" || s === "SHA512") return s;
          if (s.indexOf("SHA") === 0) return s;
          return "SHA256";
        }
        this.Date.prototype.getTimezoneOffset = function () { return 0; };
        this.setTimeout = function (fn) { if (typeof fn === "function") { try { fn(); } catch (e) {} } return 0; };
        this.setInterval = function () { return 0; };
        this.clearTimeout = function () {};
        this.clearInterval = function () {};
        this.requestAnimationFrame = function (fn) { if (typeof fn === "function") { try { fn(__dshNow()); } catch (e) {} } return 0; };
        this.addEventListener = function () {};
        this.removeEventListener = function () {};
        this.dispatchEvent = function () { return true; };
        this.matchMedia = function () {
          return { matches: false, media: "", addListener: function () {}, removeListener: function () {},
                   addEventListener: function () {}, removeEventListener: function () {} };
        };
        this.btoa = function (s) { return __dshBtoa(String(s)); };
        this.atob = function (s) { return __dshAtob(String(s)); };
        this.localStorage = {
          _d: {}, getItem: function (k) { return this._d[k] === undefined ? null : this._d[k]; },
          setItem: function (k, v) { this._d[k] = String(v); },
          removeItem: function (k) { delete this._d[k]; }, clear: function () { this._d = {}; },
          key: function () { return null; }, get length() { return Object.keys(this._d).length; }
        };
        this.sessionStorage = this.localStorage;
        this.__dshCaptured = {};
        Object.defineProperty(document, "cookie", {
          get: function () { return __dshCookieStore.join("; "); },
          set: function (v) { __dshCookieStore.push(String(v).split(";")[0]); },
          configurable: true
        });

        /* Web/host globals a real browser has and Jint does not (TextEncoder, URL, Blob, Worker,
           AudioContext, RTCPeerConnection, fetch, …). The vendor payload's bytecode VM resolves
           constructors by name from the global scope, so any missing one kills the run with
           "Cannot read properties of undefined (reading 'bind')" far away from the real cause. */
        {{WebApiShims.Prelude}}
        """;
    }

    public static string JsStr(string s)
    {
        var sb = new StringBuilder(s.Length + 2);
        sb.Append('"');
        foreach (var ch in s)
        {
            switch (ch)
            {
                case '"': sb.Append("\\\""); break;
                case '\\': sb.Append("\\\\"); break;
                case '\n': sb.Append("\\n"); break;
                case '\r': sb.Append("\\r"); break;
                case '\t': sb.Append("\\t"); break;
                default:
                    if (ch < 0x20) sb.Append($"\\u{(int)ch:x4}");
                    else sb.Append(ch);
                    break;
            }
        }
        sb.Append('"');
        return sb.ToString();
    }

    public static byte[] RandomBytes(int n) => RandomNumberGenerator.GetBytes(Math.Max(1, n));

    public static string Uuid() => Guid.NewGuid().ToString();

    public static string Btoa(string s) => Convert.ToBase64String(Encoding.UTF8.GetBytes(s));

    public static string Atob(string s)
    {
        try { return Encoding.UTF8.GetString(Convert.FromBase64String(s)); }
        catch { return string.Empty; }
    }
}
