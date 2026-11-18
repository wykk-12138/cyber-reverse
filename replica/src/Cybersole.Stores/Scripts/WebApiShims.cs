namespace Cybersole.Stores.Scripts;

/// <summary>
/// Web/host globals that a real browser has and Jint does not. The vendor payload's own bytecode VM
/// builds objects by name from the global scope via <c>Function.bind.apply</c>; when one of those
/// names is undefined the VM dies with "Cannot read properties of undefined (reading 'bind')" and
/// reports a character offset thousands of characters away from the real cause.
///
/// These are deliberately *shape* implementations, not behaviour ones: enough for a fingerprinting
/// script to read a plausible value or to construct the object, and honest about doing nothing where
/// doing something would need a real browser (Worker execution, network, WebRTC candidates).
/// Anything that must produce a specific per-run value goes through the crypto RNG in the shim
/// prelude rather than Math.random, so a run stays internally consistent.
/// </summary>
internal static class WebApiShims
{
    /// <summary>JS installed on the shim's global object, after the DOM part of the prelude.</summary>
    public const string Prelude = """
        // TEMPORARY diagnostic: the vendor payload stores every literal encoded and rebuilds them
        // with String.fromCharCode, so a plain text search of the file finds nothing. Recording the
        // decoded characters is the only way to see what the payload is actually looking for.
        this.__dshDecoded = [];
        (function () {
            var orig = String.fromCharCode;
            var rec = this.__dshDecoded;
            String.fromCharCode = function () {
                var out = orig.apply(String, arguments);
                if (rec.length < 400000) rec.push(out);
                return out;
            };
        }).call(this);

        // TEMPORARY diagnostic: the payload slices its own bytecode array with splice() right after
        // decoding the literal pool. Recording what that call removes, and what the array looks like
        // afterwards, is how we tell "the bytecode is misaligned" from "the VM asks for a slot that
        // was never assigned".
        this.__dshSplices = [];
        (function () {
            var orig = Array.prototype.splice;
            var rec = this.__dshSplices;
            Array.prototype.splice = function (start, count) {
                if (rec.length < 8) {
                    var head = [];
                    for (var i = 0; i < Math.min(24, this.length); i++) head.push(this[i]);
                    rec.push({ start: start, count: count, len: this.length, head: head });
                }
                return orig.apply(this, arguments);
            };
        }).call(this);

        // ---- TextEncoder / TextDecoder (real UTF-8, no host call needed) ----
        this.TextEncoder = function () {};
        this.TextEncoder.prototype.encode = function (s) {
            s = String(s === undefined ? "" : s);
            var out = [], i = 0;
            while (i < s.length) {
                var c = s.charCodeAt(i++);
                if (c >= 0xD800 && c <= 0xDBFF && i < s.length) {
                    var c2 = s.charCodeAt(i);
                    if (c2 >= 0xDC00 && c2 <= 0xDFFF) { c = 0x10000 + ((c - 0xD800) << 10) + (c2 - 0xDC00); i++; }
                }
                if (c < 0x80) out.push(c);
                else if (c < 0x800) out.push(0xC0 | (c >> 6), 0x80 | (c & 63));
                else if (c < 0x10000) out.push(0xE0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
                else out.push(0xF0 | (c >> 18), 0x80 | ((c >> 12) & 63), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
            }
            return new Uint8Array(out);
        };
        this.TextEncoder.prototype.encodeInto = function (s, dest) {
            var bytes = this.encode(s);
            var n = Math.min(bytes.length, dest.length);
            for (var i = 0; i < n; i++) dest[i] = bytes[i];
            return { read: s.length, written: n };
        };
        this.TextDecoder = function (label, opts) { this.encoding = (label || "utf-8").toLowerCase(); this.fatal = !!(opts && opts.fatal); };
        this.TextDecoder.prototype.decode = function (buf) {
            if (buf === undefined || buf === null) return "";
            var bytes = buf.BYTES ? buf.BYTES : buf;
            var out = "", i = 0;
            while (i < bytes.length) {
                var b = bytes[i++], c;
                if (b < 0x80) c = b;
                else if ((b & 0xE0) === 0xC0) c = ((b & 31) << 6) | (bytes[i++] & 63);
                else if ((b & 0xF0) === 0xE0) c = ((b & 15) << 12) | ((bytes[i++] & 63) << 6) | (bytes[i++] & 63);
                else c = ((b & 7) << 18) | ((bytes[i++] & 63) << 12) | ((bytes[i++] & 63) << 6) | (bytes[i++] & 63);
                if (c > 0xFFFF) { c -= 0x10000; out += String.fromCharCode(0xD800 + (c >> 10), 0xDC00 + (c & 1023)); }
                else out += String.fromCharCode(c);
            }
            return out;
        };

        // ---- URL / URLSearchParams ----
        this.URLSearchParams = function (init) {
            this._p = [];
            if (typeof init === "string") {
                init.replace(/^\?/, "").split("&").forEach(function (kv) {
                    if (!kv) return;
                    var i = kv.indexOf("=");
                    this._p.push(i < 0 ? [decodeURIComponent(kv), ""] : [decodeURIComponent(kv.slice(0, i)), decodeURIComponent(kv.slice(i + 1))]);
                }, this);
            } else if (init && init.length !== undefined) {
                for (var i = 0; i < init.length; i++) this._p.push([String(init[i][0]), String(init[i][1])]);
            }
        };
        this.URLSearchParams.prototype.get = function (k) { for (var i = 0; i < this._p.length; i++) if (this._p[i][0] === k) return this._p[i][1]; return null; };
        this.URLSearchParams.prototype.getAll = function (k) { var r = []; for (var i = 0; i < this._p.length; i++) if (this._p[i][0] === k) r.push(this._p[i][1]); return r; };
        this.URLSearchParams.prototype.has = function (k) { return this.get(k) !== null; };
        this.URLSearchParams.prototype.append = function (k, v) { this._p.push([String(k), String(v)]); };
        this.URLSearchParams.prototype.set = function (k, v) { this.delete(k); this.append(k, v); };
        this.URLSearchParams.prototype["delete"] = function (k) { this._p = this._p.filter(function (x) { return x[0] !== k; }); };
        this.URLSearchParams.prototype.toString = function () { return this._p.map(function (x) { return encodeURIComponent(x[0]) + "=" + encodeURIComponent(x[1]); }).join("&"); };
        this.URLSearchParams.prototype.forEach = function (fn, self) { this._p.forEach(function (x) { fn.call(self, x[1], x[0], this); }, this); };

        var __dshParseUrl = function (raw, base) {
            raw = String(raw);
            var m = /^([a-zA-Z][a-zA-Z0-9+.\-]*):(?:\/\/([^\/?#]*))?([^?#]*)(?:\?([^#]*))?(?:#(.*))?$/.exec(raw);
            if (!m && base) {
                var b = (base instanceof URL) ? base : new URL(String(base));
                if (raw.charAt(0) === "/") { return __dshParseUrl(b.protocol + "//" + b.host + raw, null); }
                if (raw.charAt(0) === "#") { return __dshParseUrl(b.href.split("#")[0] + raw, null); }
                if (raw.charAt(0) === "?") { return __dshParseUrl(b.protocol + "//" + b.host + b.pathname + raw, null); }
                var dir = b.pathname.replace(/[^\/]*$/, "");
                return __dshParseUrl(b.protocol + "//" + b.host + dir + raw, null);
            }
            if (!m) return null;
            var auth = m[2] || "";
            var at = auth.indexOf("@");
            var userinfo = at >= 0 ? auth.slice(0, at) : "";
            var hostport = at >= 0 ? auth.slice(at + 1) : auth;
            var colon = hostport.lastIndexOf(":");
            var port = colon > 0 && hostport.indexOf("]") < colon ? hostport.slice(colon + 1) : "";
            var host = colon > 0 && hostport.indexOf("]") < colon ? hostport.slice(0, colon) : hostport;
            return { protocol: (m[1] || "") + ":", username: userinfo.split(":")[0] || "", password: userinfo.split(":")[1] || "",
                     host: host + (port ? ":" + port : ""), hostname: host, port: port, pathname: m[3] || "/",
                     search: m[4] !== undefined ? "?" + m[4] : "", hash: m[5] !== undefined ? "#" + m[5] : "" };
        };
        this.URL = function (raw, base) {
            var u = __dshParseUrl(raw, base);
            if (!u) throw new TypeError("Invalid URL");
            this.protocol = u.protocol; this.username = u.username; this.password = u.password;
            this.host = u.host; this.hostname = u.hostname; this.port = u.port;
            this.pathname = u.pathname; this.search = u.search; this.hash = u.hash;
            this.searchParams = new URLSearchParams(u.search);
            this.origin = u.protocol + "//" + u.host;
        };
        Object.defineProperty(this.URL.prototype, "href", {
            get: function () { return this.origin + this.pathname + this.search + this.hash; },
            set: function (v) { var u = __dshParseUrl(v, null); if (u) { this.protocol = u.protocol; this.host = u.host; this.hostname = u.hostname; this.port = u.port; this.pathname = u.pathname; this.search = u.search; this.hash = u.hash; } }
        });
        this.URL.prototype.toString = function () { return this.href; };
        this.URL.createObjectURL = function (blob) { blob._url = "blob:" + (this && this.origin ? this.origin : "https://localhost") + "/" + __dshUuid(); return blob._url; };
        this.URL.revokeObjectURL = function () {};
        this.webkitURL = this.URL;

        // ---- Blob / File / FileReader ----
        this.Blob = function (parts, opts) {
            this.parts = parts || []; this.type = (opts && opts.type) || "";
            this.size = 0;
            for (var i = 0; i < this.parts.length; i++) {
                var p = this.parts[i];
                this.size += p && p.length !== undefined ? p.length : String(p).length;
            }
        };
        this.Blob.prototype.slice = function (a, b, t) { return new Blob(this.parts, { type: t || this.type }); };
        this.Blob.prototype.text = function () { return Promise.resolve(this.parts.map(function (p) { return String(p); }).join("")); };
        this.Blob.prototype.arrayBuffer = function () { return Promise.resolve(new TextEncoder().encode(this.parts.map(function (p) { return String(p); }).join("")).buffer); };
        this.File = function (parts, name, opts) { Blob.call(this, parts, opts); this.name = name; this.lastModified = (opts && opts.lastModified) || Date.now(); };
        this.File.prototype = Object.create(this.Blob.prototype);
        this.FileReader = function () { this.result = null; this.readyState = 0; this.error = null; };
        this.FileReader.prototype.readAsText = function (b) { this.readyState = 2; this.result = b && b.parts ? b.parts.join("") : String(b); if (this.onload) this.onload({ target: this }); };
        this.FileReader.prototype.readAsDataURL = function (b) { this.readyState = 2; this.result = "data:" + ((b && b.type) || "application/octet-stream") + ";base64," + btoa(b && b.parts ? b.parts.join("") : String(b)); if (this.onload) this.onload({ target: this }); };
        this.FileReader.prototype.readAsArrayBuffer = function (b) { this.readyState = 2; this.result = new TextEncoder().encode(b && b.parts ? b.parts.join("") : String(b)).buffer; if (this.onload) this.onload({ target: this }); };
        this.FileReader.prototype.abort = function () {};

        // ---- timers / microtasks ----
        this.queueMicrotask = function (fn) { try { fn(); } catch (e) {} };
        this.requestIdleCallback = function (fn) { try { fn({ didTimeout: false, timeRemaining: function () { return 50; } }); } catch (e) {} return 0; };
        this.cancelIdleCallback = function () {};
        this.structuredClone = function (v) { return v === undefined ? undefined : JSON.parse(JSON.stringify(v)); };

        // ---- AbortController / AbortSignal ----
        this.AbortSignal = function () { this.aborted = false; this.onabort = null; };
        this.AbortSignal.prototype.addEventListener = function () {};
        this.AbortSignal.prototype.removeEventListener = function () {};
        this.AbortSignal.abort = function () { var s = new AbortSignal(); s.aborted = true; return s; };
        this.AbortController = function () { this.signal = new AbortSignal(); };
        this.AbortController.prototype.abort = function () { this.signal.aborted = true; if (this.signal.onabort) this.signal.onabort(); };

        // ---- events ----
        this.Event = function (type, init) { this.type = type; this.bubbles = !!(init && init.bubbles); this.cancelable = !!(init && init.cancelable); this.defaultPrevented = false; };
        this.Event.prototype.preventDefault = function () { this.defaultPrevented = true; };
        this.Event.prototype.stopPropagation = function () {};
        this.Event.prototype.stopImmediatePropagation = function () {};
        this.CustomEvent = function (type, init) { Event.call(this, type, init); this.detail = init && init.detail; };
        this.CustomEvent.prototype = Object.create(this.Event.prototype);
        this.EventTarget = function () { this._l = {}; };
        this.EventTarget.prototype.addEventListener = function (t, fn) { (this._l[t] = this._l[t] || []).push(fn); };
        this.EventTarget.prototype.removeEventListener = function (t, fn) { var a = this._l[t]; if (a) { var i = a.indexOf(fn); if (i >= 0) a.splice(i, 1); } };
        this.EventTarget.prototype.dispatchEvent = function (e) { var a = this._l[e.type] || []; for (var i = 0; i < a.length; i++) { try { a[i](e); } catch (x) {} } return true; };

        // ---- Image / ImageData / Path2D / createImageBitmap ----
        this.ImageData = function (a, b, c) {
            if (a && a.length !== undefined) { this.data = a; this.width = b; this.height = c; }
            else { this.width = a; this.height = b; this.data = new Uint8ClampedArray(a * b * 4); }
            this.colorSpace = "srgb";
        };
        this.Image = function (w, h) {
            var self = this;
            this.width = w || 0; this.height = h || 0; this.src = ""; this.complete = false;
            this.naturalWidth = 0; this.naturalHeight = 0;
            this.onload = null; this.onerror = null;
            this.addEventListener = function () {}; this.removeEventListener = function () {};
            this.decode = function () { return Promise.resolve(); };
            Object.defineProperty(this, "src", {
                get: function () { return self._src || ""; },
                set: function (v) { self._src = v; self.complete = true; self.width = self.width || 1; self.height = self.height || 1; self.naturalWidth = self.width; self.naturalHeight = self.height; if (self.onload) self.onload({ target: self }); }
            });
        };
        this.Path2D = function () { this._ops = []; };
        ["moveTo", "lineTo", "rect", "arc", "bezierCurveTo", "quadraticCurveTo", "closePath", "ellipse", "arcTo"].forEach(function (m) {
            Path2D.prototype[m] = function () { this._ops.push([m].concat([].slice.call(arguments))); };
        });
        this.createImageBitmap = function (src) {
            var w = (src && (src.width || src.naturalWidth)) || 1, h = (src && (src.height || src.naturalHeight)) || 1;
            return Promise.resolve({ width: w, height: h, close: function () {} });
        };

        // ---- audio / webrtc: values a fingerprinting script reads, not a working stack ----
        this.AudioContext = function () {
            this.sampleRate = 48000; this.currentTime = 0; this.state = "running";
            this.baseLatency = 0.01; this.outputLatency = 0.01; this.destination = { maxChannelCount: 2, numberOfInputs: 0, numberOfOutputs: 0, channelCount: 2 };
        };
        this.AudioContext.prototype.createOscillator = function () { return { type: "sine", frequency: { value: 440, setValueAtTime: function () {} }, connect: function () {}, start: function () {}, stop: function () {}, disconnect: function () {} }; };
        this.AudioContext.prototype.createAnalyser = function () { return { fftSize: 2048, frequencyBinCount: 1024, getByteFrequencyData: function (a) { for (var i = 0; i < a.length; i++) a[i] = 0; }, getFloatFrequencyData: function (a) { for (var i = 0; i < a.length; i++) a[i] = -100; }, connect: function () {}, disconnect: function () {} }; };
        this.AudioContext.prototype.createDynamicsCompressor = function () { return { threshold: { value: -24 }, knee: { value: 30 }, ratio: { value: 12 }, attack: { value: 0.003 }, release: { value: 0.25 }, reduction: 0, connect: function () {}, disconnect: function () {} }; };
        this.AudioContext.prototype.createGain = function () { return { gain: { value: 1, setValueAtTime: function () {} }, connect: function () {}, disconnect: function () {} }; };
        this.AudioContext.prototype.createBuffer = function (ch, len, rate) { return { numberOfChannels: ch, length: len, sampleRate: rate, duration: len / rate, getChannelData: function () { return new Float32Array(len); } }; };
        this.AudioContext.prototype.createBufferSource = function () { return { buffer: null, connect: function () {}, start: function () {}, stop: function () {}, disconnect: function () {} }; };
        this.AudioContext.prototype.createScriptProcessor = function () { return { connect: function () {}, disconnect: function () {} }; };
        this.AudioContext.prototype.createMediaStreamDestination = function () { return { stream: { getTracks: function () { return []; } }, connect: function () {} }; };
        this.AudioContext.prototype.resume = function () { return Promise.resolve(); };
        this.AudioContext.prototype.close = function () { return Promise.resolve(); };
        this.AudioContext.prototype.decodeAudioData = function () { return Promise.reject(new Error("decodeAudioData unsupported")); };
        this.webkitAudioContext = this.AudioContext;
        this.OfflineAudioContext = function () { AudioContext.call(this); };

        this.RTCPeerConnection = function () {
            this.localDescription = null; this.remoteDescription = null;
            this.iceConnectionState = "new"; this.iceGatheringState = "new"; this.connectionState = "new"; this.signalingState = "stable";
            this.onicecandidate = null; this.onicegatheringstatechange = null; this.ondatachannel = null;
        };
        this.RTCPeerConnection.prototype.createDataChannel = function (label) { return { label: label, readyState: "connecting", send: function () {}, close: function () {}, addEventListener: function () {} }; };
        this.RTCPeerConnection.prototype.createOffer = function () { return Promise.resolve({ type: "offer", sdp: "v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\n" }); };
        this.RTCPeerConnection.prototype.createAnswer = function () { return Promise.resolve({ type: "answer", sdp: "v=0\r\n" }); };
        this.RTCPeerConnection.prototype.setLocalDescription = function (d) { this.localDescription = d; return Promise.resolve(); };
        this.RTCPeerConnection.prototype.setRemoteDescription = function (d) { this.remoteDescription = d; return Promise.resolve(); };
        this.RTCPeerConnection.prototype.addIceCandidate = function () { return Promise.resolve(); };
        this.RTCPeerConnection.prototype.getStats = function () { return Promise.resolve({ forEach: function () {} }); };
        this.RTCPeerConnection.prototype.getSenders = function () { return []; };
        this.RTCPeerConnection.prototype.getTransceivers = function () { return []; };
        this.RTCPeerConnection.prototype.close = function () { this.connectionState = "closed"; };
        this.RTCPeerConnection.prototype.addEventListener = function () {};
        this.RTCPeerConnection.prototype.removeEventListener = function () {};
        this.webkitRTCPeerConnection = this.RTCPeerConnection;
        this.RTCSessionDescription = function (init) { this.type = init && init.type; this.sdp = init && init.sdp; };
        this.RTCIceCandidate = function (init) { this.candidate = init && init.candidate; };

        // ---- workers: constructible and message-shaped, but they do not execute ----
        this.Worker = function (url, opts) {
            this.onmessage = null; this.onerror = null; this._url = String(url);
            var self = this;
            this.postMessage = function (data) {
                if (self.onmessage) { try { self.onmessage({ data: data }); } catch (e) {} }
            };
            this.terminate = function () {};
            this.addEventListener = function (t, fn) { if (t === "message") self.onmessage = fn; };
            this.removeEventListener = function () {};
        };
        this.SharedWorker = this.Worker;
        this.MessageChannel = function () {
            var self = this;
            this.port1 = { onmessage: null, postMessage: function (d) { if (self.port2.onmessage) { try { self.port2.onmessage({ data: d }); } catch (e) {} } }, start: function () {}, close: function () {}, addEventListener: function (t, fn) { if (t === "message") this.onmessage = fn; } };
            this.port2 = { onmessage: null, postMessage: function (d) { if (self.port1.onmessage) { try { self.port1.onmessage({ data: d }); } catch (e) {} } }, start: function () {}, close: function () {}, addEventListener: function (t, fn) { if (t === "message") this.onmessage = fn; } };
        };
        this.MessagePort = function () { return new MessageChannel().port1; };
        this.BroadcastChannel = function (name) { this.name = name; this.onmessage = null; this.postMessage = function () {}; this.close = function () {}; this.addEventListener = function () {}; };
        this.importScripts = function () {};
        this.postMessage = function () {};

        // ---- network: never actually reached from a solver run ----
        this.fetch = function () { return Promise.reject(new TypeError("fetch is not available in this sandbox")); };
        this.Headers = function () { this._h = {}; };
        this.Headers.prototype.get = function (k) { return this._h[String(k).toLowerCase()] || null; };
        this.Headers.prototype.set = function (k, v) { this._h[String(k).toLowerCase()] = String(v); };
        this.Headers.prototype.has = function (k) { return this.get(k) !== null; };
        this.Request = function (url) { this.url = String(url); this.method = "GET"; this.headers = new Headers(); };
        this.Response = function (body, init) { this.body = body; this.status = (init && init.status) || 200; this.ok = this.status >= 200 && this.status < 300; this.headers = new Headers(); this.text = function () { return Promise.resolve(String(body === undefined ? "" : body)); }; this.json = function () { return Promise.resolve(JSON.parse(body)); }; };
        this.XMLHttpRequest = function () {
            this.readyState = 0; this.status = 0; this.responseText = ""; this.response = null;
            this.onreadystatechange = null; this.onload = null; this.onerror = null;
            this.open = function () { this.readyState = 1; };
            this.setRequestHeader = function () {};
            this.getAllResponseHeaders = function () { return ""; };
            this.getResponseHeader = function () { return null; };
            this.send = function () { this.readyState = 4; this.status = 0; if (this.onerror) this.onerror({}); };
            this.abort = function () {};
            this.addEventListener = function () {};
        };
        this.WebSocket = function (url) {
            this.url = String(url); this.readyState = 0; this.onopen = null; this.onmessage = null; this.onerror = null; this.onclose = null;
            var self = this;
            this.send = function () {};
            this.close = function () { self.readyState = 3; };
            this.addEventListener = function () {};
        };
        this.WebSocket.CONNECTING = 0; this.WebSocket.OPEN = 1; this.WebSocket.CLOSING = 2; this.WebSocket.CLOSED = 3;
        this.WebAssembly = { compile: function () { return Promise.reject(new Error("WebAssembly unavailable")); }, instantiate: function () { return Promise.reject(new Error("WebAssembly unavailable")); }, validate: function () { return false; }, Module: function () {}, Instance: function () {}, Memory: function () { this.buffer = new ArrayBuffer(65536); } };

        // ---- misc host surfaces ----
        this.Notification = function () {}; this.Notification.permission = "default"; this.Notification.requestPermission = function () { return Promise.resolve("default"); };
        this.Permissions = function () {}; this.permissions = { query: function () { return Promise.resolve({ state: "prompt", onchange: null }); } };
        this.indexedDB = { open: function () { return { onsuccess: null, onerror: null, onupgradeneeded: null, result: { createObjectStore: function () { return {}; }, transaction: function () { return { objectStore: function () { return { get: function () { return {}; }, put: function () {}, add: function () {}, delete: function () {}, getAll: function () { return {}; } }; } }; } } }; } };
        this.caches = { open: function () { return Promise.resolve({ match: function () { return Promise.resolve(undefined); }, put: function () { return Promise.resolve(); }, addAll: function () { return Promise.resolve(); }, keys: function () { return Promise.resolve([]); } }); }, keys: function () { return Promise.resolve([]); }, match: function () { return Promise.resolve(undefined); } };
        ["PerformanceObserver", "IntersectionObserver", "ResizeObserver", "MutationObserver"].forEach(function (name) {
            this[name] = function (cb) { this.observe = function () {}; this.unobserve = function () {}; this.disconnect = function () {}; this.takeRecords = function () { return []; }; };
        }, this);
        this.DOMParser = function () {};
        this.DOMParser.prototype.parseFromString = function (text, type) { return this.documentElement || { nodeType: 9, documentElement: { nodeType: 1, childNodes: [], innerHTML: String(text), textContent: String(text), querySelector: function () { return null; }, querySelectorAll: function () { return []; }, getElementsByTagName: function () { return []; } }, querySelector: function () { return null; }, querySelectorAll: function () { return []; } }; };
        this.XPathResult = { ANY_TYPE: 0, NUMBER_TYPE: 1, STRING_TYPE: 2, BOOLEAN_TYPE: 3, UNORDERED_NODE_ITERATOR_TYPE: 4, ORDERED_NODE_SNAPSHOT_TYPE: 7, ANY_UNORDERED_NODE_TYPE: 8 };
        this.getComputedStyle = function (el) { return { getPropertyValue: function () { return ""; }, length: 0, item: function () { return ""; }, cssText: "" }; };
        """;
}
