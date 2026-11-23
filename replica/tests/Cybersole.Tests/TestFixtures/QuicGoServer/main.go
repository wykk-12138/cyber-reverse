package main

import (
	"bufio"
	"bytes"
	"context"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/sha256"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"flag"
	"fmt"
	"io"
	"math/big"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/quic-go/quic-go"
	"github.com/quic-go/quic-go/http3"
	"golang.org/x/net/http2"
)

type ctxKey int

const (
	ctxKeyConnCapture ctxKey = iota + 1
	ctxKeyTLSState
)

type tcpConnCapture struct {
	mu              sync.Mutex
	rawHelloBuf     bytes.Buffer
	clientHelloDone bool
	clientHelloMsg  []byte
	rawH2Buf        bytes.Buffer
	h2CaptureDone   bool
	h2PrefaceBytes  []byte
	tlsState        tls.ConnectionState
	hasTLSState     bool
}

type quicInitialInfo struct {
	InitialCount          int
	FirstDatagramLen      int
	FirstDcidLen          int
	FirstScidLen          int
	SawRetryTokenInitial  bool
	LastInitialTokenLen   int
}

type quicTracker struct {
	mu     sync.Mutex
	byAddr map[string]*quicInitialInfo
}

func newQuicTracker() *quicTracker {
	return &quicTracker{byAddr: make(map[string]*quicInitialInfo)}
}

func (qt *quicTracker) record(addr string, pkt []byte) {
	if len(pkt) < 7 || (pkt[0]&0x80) == 0 {
		return
	}
	pktType := (pkt[0] & 0x30) >> 4
	ver := binary.BigEndian.Uint32(pkt[1:5])
	if ver != 1 || pktType != 0 {
		return
	}
	dcidLen := int(pkt[5])
	off := 6 + dcidLen
	if off >= len(pkt) {
		return
	}
	scidLen := int(pkt[off])
	off += 1 + scidLen
	tokenLen := 0
	if off < len(pkt) {
		b0 := pkt[off]
		prefix := b0 >> 6
		vlen := 1 << prefix
		if off+vlen <= len(pkt) {
			var v uint64
			for i := 0; i < vlen; i++ {
				val := pkt[off+i]
				if i == 0 {
					val &= 0x3f
				}
				v = (v << 8) | uint64(val)
			}
			tokenLen = int(v)
		}
	}

	qt.mu.Lock()
	defer qt.mu.Unlock()
	info := qt.byAddr[addr]
	if info == nil {
		info = &quicInitialInfo{
			FirstDatagramLen: len(pkt),
			FirstDcidLen:     dcidLen,
			FirstScidLen:     scidLen,
		}
		qt.byAddr[addr] = info
	}
	info.InitialCount++
	info.LastInitialTokenLen = tokenLen
	if tokenLen > 0 {
		info.SawRetryTokenInitial = true
	}
}

func (qt *quicTracker) snapshot(addr string) *quicInitialInfo {
	qt.mu.Lock()
	defer qt.mu.Unlock()
	info := qt.byAddr[addr]
	if info == nil {
		return nil
	}
	cp := *info
	return &cp
}

type quicCapturePacketConn struct {
	net.PacketConn
	tracker *quicTracker
}

func (q *quicCapturePacketConn) ReadFrom(p []byte) (int, net.Addr, error) {
	n, addr, err := q.PacketConn.ReadFrom(p)
	if n > 0 && addr != nil {
		q.tracker.record(addr.String(), p[:n])
	}
	return n, addr, err
}

type clientHelloCaptureConn struct {
	net.Conn
	cap *tcpConnCapture
}

func (c *clientHelloCaptureConn) Read(b []byte) (int, error) {
	n, err := c.Conn.Read(b)
	if n > 0 {
		c.cap.mu.Lock()
		if !c.cap.clientHelloDone && c.cap.rawHelloBuf.Len() < 32768 {
			c.cap.rawHelloBuf.Write(b[:n])
			if msg := tryExtractFirstHandshakeClientHello(c.cap.rawHelloBuf.Bytes()); len(msg) > 0 {
				c.cap.clientHelloMsg = msg
				c.cap.clientHelloDone = true
			}
		}
		c.cap.mu.Unlock()
	}
	return n, err
}

func tryExtractFirstHandshakeClientHello(records []byte) []byte {
	var hs bytes.Buffer
	off := 0
	for off+5 <= len(records) {
		recType := records[off]
		recLen := int(binary.BigEndian.Uint16(records[off+3 : off+5]))
		if recType != 0x16 || off+5+recLen > len(records) {
			break
		}
		hs.Write(records[off+5 : off+5+recLen])
		off += 5 + recLen
		raw := hs.Bytes()
		if len(raw) >= 4 && raw[0] == 0x01 {
			msgLen := (int(raw[1]) << 16) | (int(raw[2]) << 8) | int(raw[3])
			if len(raw) >= 4+msgLen {
				out := make([]byte, 4+msgLen)
				copy(out, raw[:4+msgLen])
				return out
			}
		}
	}
	return nil
}

type h2PrefaceCaptureConn struct {
	net.Conn
	cap *tcpConnCapture
}

var http2ClientPreface = []byte("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n")

func (c *h2PrefaceCaptureConn) Read(b []byte) (int, error) {
	n, err := c.Conn.Read(b)
	if n > 0 {
		c.cap.mu.Lock()
		if !c.cap.h2CaptureDone && c.cap.rawH2Buf.Len() < 16384 {
			c.cap.rawH2Buf.Write(b[:n])
			if pref := tryExtractH2PrefaceBurst(c.cap.rawH2Buf.Bytes()); len(pref) > 0 {
				c.cap.h2PrefaceBytes = pref
				c.cap.h2CaptureDone = true
			}
		}
		c.cap.mu.Unlock()
	}
	return n, err
}

func tryExtractH2PrefaceBurst(buf []byte) []byte {
	if !bytes.HasPrefix(buf, http2ClientPreface) {
		return nil
	}
	off := len(http2ClientPreface)
	lastValid := 0
	for off+9 <= len(buf) {
		fLen := (int(buf[off]) << 16) | (int(buf[off+1]) << 8) | int(buf[off+2])
		fType := buf[off+3]
		fFlags := buf[off+4]
		if off+9+fLen > len(buf) {
			break
		}
		isPrefaceFrame := (fType == 0x04 && (fFlags&0x01) == 0) || fType == 0x08 || fType == 0x02
		if !isPrefaceFrame {
			out := make([]byte, off)
			copy(out, buf[:off])
			return out
		}
		off += 9 + fLen
		lastValid = off
	}
	_ = lastValid
	return nil
}

type inspectResponse struct {
	ServerRole         string              `json:"serverRole"`
	Proto              string              `json:"proto"`
	Method             string              `json:"method"`
	Path               string              `json:"path"`
	RemoteAddr         string              `json:"remoteAddr"`
	UserAgent          string              `json:"userAgent"`
	HasUserAgent       bool                `json:"hasUserAgent"`
	TlsVersion         uint16              `json:"tlsVersion"`
	CipherSuite        uint16              `json:"cipherSuite"`
	CurveID            uint16              `json:"curveId"`
	CurveName          string              `json:"curveName"`
	DidResume          bool                `json:"didResume"`
	HelloRetryRequest  bool                `json:"helloRetryRequest"`
	NegotiatedProtocol string              `json:"negotiatedProtocol"`
	ServerName         string              `json:"serverName"`
	ClientHelloHex     string              `json:"clientHelloHex,omitempty"`
	H2PrefaceHex       string              `json:"h2PrefaceHex,omitempty"`
	Quic               *quicInitialInfo    `json:"quic,omitempty"`
	Headers            map[string][]string `json:"headers"`
}

func generateEphemeralCerts(caOutPath string) (tls.Certificate, error) {
	caKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return tls.Certificate{}, err
	}
	now := time.Now().UTC()
	caSerial, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 120))
	if err != nil {
		return tls.Certificate{}, err
	}
	caTmpl := &x509.Certificate{
		SerialNumber: caSerial,
		Subject: pkix.Name{
			CommonName:   "Cybersole Go Interop Test Root CA",
			Organization: []string{"Cybersole Interop Fixture"},
		},
		NotBefore:             now.Add(-1 * time.Hour),
		NotAfter:              now.Add(48 * time.Hour),
		KeyUsage:              x509.KeyUsageCertSign | x509.KeyUsageCRLSign | x509.KeyUsageDigitalSignature,
		BasicConstraintsValid: true,
		IsCA:                  true,
	}
	caDER, err := x509.CreateCertificate(rand.Reader, caTmpl, caTmpl, &caKey.PublicKey, caKey)
	if err != nil {
		return tls.Certificate{}, err
	}
	caParsed, err := x509.ParseCertificate(caDER)
	if err != nil {
		return tls.Certificate{}, err
	}

	if caOutPath != "" {
		pemBytes := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: caDER})
		if err := os.WriteFile(caOutPath, pemBytes, 0o644); err != nil {
			return tls.Certificate{}, err
		}
	}

	leafKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return tls.Certificate{}, err
	}
	leafSerial, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 120))
	if err != nil {
		return tls.Certificate{}, err
	}
	leafTmpl := &x509.Certificate{
		SerialNumber: leafSerial,
		Subject: pkix.Name{
			CommonName: "localhost",
		},
		NotBefore:   now.Add(-1 * time.Hour),
		NotAfter:    now.Add(48 * time.Hour),
		KeyUsage:    x509.KeyUsageDigitalSignature,
		ExtKeyUsage: []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		DNSNames:    []string{"localhost"},
		IPAddresses: []net.IP{net.ParseIP("127.0.0.1"), net.ParseIP("::1")},
	}
	leafDER, err := x509.CreateCertificate(rand.Reader, leafTmpl, caParsed, &leafKey.PublicKey, caKey)
	if err != nil {
		return tls.Certificate{}, err
	}

	return tls.Certificate{
		Certificate: [][]byte{leafDER, caDER},
		PrivateKey:  leafKey,
	}, nil
}

func makeHandler(role string, qt *quicTracker) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("/inspect", func(w http.ResponseWriter, r *http.Request) {
		var cs tls.ConnectionState
		var hasState bool
		var chHex, h2Hex string

		if v := r.Context().Value(ctxKeyConnCapture); v != nil {
			cap := v.(*tcpConnCapture)
			cap.mu.Lock()
			if len(cap.clientHelloMsg) > 0 {
				chHex = hex.EncodeToString(cap.clientHelloMsg)
			}
			if len(cap.h2PrefaceBytes) > 0 {
				h2Hex = hex.EncodeToString(cap.h2PrefaceBytes)
			} else if cap.rawH2Buf.Len() > 0 {
				if pref := tryExtractH2PrefaceBurst(cap.rawH2Buf.Bytes()); len(pref) > 0 {
					h2Hex = hex.EncodeToString(pref)
				}
			}
			if cap.hasTLSState {
				cs = cap.tlsState
				hasState = true
			}
			cap.mu.Unlock()
		}
		if !hasState {
			if v := r.Context().Value(ctxKeyTLSState); v != nil {
				cs = v.(tls.ConnectionState)
				hasState = true
			} else if r.TLS != nil {
				cs = *r.TLS
				hasState = true
			}
		}

		hdrs := make(map[string][]string, len(r.Header))
		for k, vals := range r.Header {
			cp := make([]string, len(vals))
			copy(cp, vals)
			hdrs[k] = cp
		}
		_, hasUA := r.Header["User-Agent"]

		resp := inspectResponse{
			ServerRole:   role,
			Proto:        r.Proto,
			Method:       r.Method,
			Path:         r.URL.RequestURI(),
			RemoteAddr:   r.RemoteAddr,
			UserAgent:    r.UserAgent(),
			HasUserAgent: hasUA,
			Headers:      hdrs,
			ClientHelloHex: chHex,
			H2PrefaceHex:   h2Hex,
		}
		if hasState {
			resp.TlsVersion = cs.Version
			resp.CipherSuite = cs.CipherSuite
			resp.CurveID = uint16(cs.CurveID)
			resp.CurveName = cs.CurveID.String()
			resp.DidResume = cs.DidResume
			resp.HelloRetryRequest = cs.HelloRetryRequest
			resp.NegotiatedProtocol = cs.NegotiatedProtocol
			resp.ServerName = cs.ServerName
		}
		if qt != nil {
			resp.Quic = qt.snapshot(r.RemoteAddr)
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_ = json.NewEncoder(w).Encode(resp)
	})

	mux.HandleFunc("/large", func(w http.ResponseWriter, r *http.Request) {
		size := 512 * 1024
		if raw := r.URL.Query().Get("bytes"); raw != "" {
			if parsed, err := strconv.Atoi(raw); err == nil && parsed > 0 && parsed <= 4*1024*1024 {
				size = parsed
			}
		}
		payload := make([]byte, size)
		for i := range payload {
			payload[i] = byte((i*31 + 17) & 0xff)
		}
		sum := sha256.Sum256(payload)
		w.Header().Set("Content-Type", "application/octet-stream")
		w.Header().Set("X-Payload-Sha256", hex.EncodeToString(sum[:]))
		w.Header().Set("Content-Length", strconv.Itoa(len(payload)))
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write(payload)
	})

	mux.HandleFunc("/echo", func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		sum := sha256.Sum256(body)
		w.Header().Set("Content-Type", "application/octet-stream")
		w.Header().Set("X-Echo-Method", r.Method)
		w.Header().Set("X-Echo-Length", strconv.Itoa(len(body)))
		w.Header().Set("X-Echo-Sha256", hex.EncodeToString(sum[:]))
		w.Header().Set("X-Echo-Proto", r.Proto)
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write(body)
	})

	return mux
}

func serveTCPListener(ctx context.Context, ln net.Listener, baseTLS *tls.Config, role string) {
	h2Srv := &http2.Server{}
	mux := makeHandler(role, nil)

	for {
		rawConn, err := ln.Accept()
		if err != nil {
			return
		}
		go func(c net.Conn) {
			defer c.Close()
			cap := &tcpConnCapture{}
			rawCap := &clientHelloCaptureConn{Conn: c, cap: cap}
			tlsConn := tls.Server(rawCap, baseTLS)
			defer tlsConn.Close()

			hsCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
			err := tlsConn.HandshakeContext(hsCtx)
			cancel()
			if err != nil {
				return
			}

			cs := tlsConn.ConnectionState()
			cap.mu.Lock()
			cap.tlsState = cs
			cap.hasTLSState = true
			cap.mu.Unlock()

			reqCtx := context.WithValue(ctx, ctxKeyConnCapture, cap)
			if cs.NegotiatedProtocol == "h2" {
				h2Cap := &h2PrefaceCaptureConn{Conn: tlsConn, cap: cap}
				h2Srv.ServeConn(h2Cap, &http2.ServeConnOpts{
					Context: reqCtx,
					Handler: mux,
				})
				return
			}

			// Fallback HTTP/1.1 handling for single TLS connection
			br := bufio.NewReader(tlsConn)
			for {
				req, err := http.ReadRequest(br)
				if err != nil {
					return
				}
				req = req.WithContext(reqCtx)
				rw := newSingleH1ResponseWriter(tlsConn)
				mux.ServeHTTP(rw, req)
				if err := rw.finish(req.Close); err != nil || req.Close {
					return
				}
			}
		}(rawConn)
	}
}

type singleH1ResponseWriter struct {
	w          io.Writer
	hdr        http.Header
	buf        bytes.Buffer
	statusCode int
}

func newSingleH1ResponseWriter(w io.Writer) *singleH1ResponseWriter {
	return &singleH1ResponseWriter{w: w, hdr: make(http.Header), statusCode: http.StatusOK}
}

func (s *singleH1ResponseWriter) Header() http.Header { return s.hdr }
func (s *singleH1ResponseWriter) WriteHeader(code int) {
	s.statusCode = code
}
func (s *singleH1ResponseWriter) Write(p []byte) (int, error) {
	return s.buf.Write(p)
}
func (s *singleH1ResponseWriter) finish(closeConn bool) error {
	var out bytes.Buffer
	fmt.Fprintf(&out, "HTTP/1.1 %d %s\r\n", s.statusCode, http.StatusText(s.statusCode))
	if s.hdr.Get("Content-Length") == "" {
		s.hdr.Set("Content-Length", strconv.Itoa(s.buf.Len()))
	}
	if closeConn {
		s.hdr.Set("Connection", "close")
	}
	_ = s.hdr.Write(&out)
	out.WriteString("\r\n")
	out.Write(s.buf.Bytes())
	_, err := s.w.Write(out.Bytes())
	return err
}

func startH3Server(
	ctx context.Context,
	pc net.PacketConn,
	tlsConf *tls.Config,
	role string,
	forceRetry bool,
) (*http3.Server, error) {
	qt := newQuicTracker()
	trackedPC := &quicCapturePacketConn{PacketConn: pc, tracker: qt}
	tr := &quic.Transport{Conn: trackedPC}
	if forceRetry {
		tr.VerifySourceAddress = func(net.Addr) bool { return true }
	}
	ln, err := tr.ListenEarly(http3.ConfigureTLSConfig(tlsConf), &quic.Config{
		Allow0RTT: false,
	})
	if err != nil {
		return nil, err
	}

	h3Srv := &http3.Server{
		TLSConfig: http3.ConfigureTLSConfig(tlsConf),
		Handler:   makeHandler(role, qt),
		ConnContext: func(cctx context.Context, c *quic.Conn) context.Context {
			return context.WithValue(cctx, ctxKeyTLSState, c.ConnectionState().TLS)
		},
	}

	go func() {
		<-ctx.Done()
		_ = h3Srv.Close()
		_ = ln.Close()
		_ = tr.Close()
	}()
	go func() {
		_ = h3Srv.ServeListener(ln)
	}()
	return h3Srv, nil
}

func bindDualPort() (net.Listener, net.PacketConn, string, error) {
	for i := 0; i < 32; i++ {
		tcpLn, err := net.Listen("tcp", "127.0.0.1:0")
		if err != nil {
			return nil, nil, "", err
		}
		addr := tcpLn.Addr().String()
		udpPC, err := net.ListenPacket("udp", addr)
		if err == nil {
			return tcpLn, udpPC, addr, nil
		}
		_ = tcpLn.Close()
	}
	return nil, nil, "", fmt.Errorf("failed to bind matching TCP+UDP port")
}

func main() {
	caOut := flag.String("ca-out", "", "Path to write ephemeral CA certificate PEM")
	flag.Parse()

	cert, err := generateEphemeralCerts(*caOut)
	if err != nil {
		fmt.Fprintf(os.Stderr, "cert generation failed: %v\n", err)
		os.Exit(1)
	}

	var sessionTicketKey [32]byte
	_, _ = io.ReadFull(rand.Reader, sessionTicketKey[:])

	mainTLS := &tls.Config{
		Certificates:     []tls.Certificate{cert},
		NextProtos:       []string{"h2", "http/1.1"},
		MinVersion:       tls.VersionTLS12,
		MaxVersion:       tls.VersionTLS13,
		CurvePreferences: []tls.CurveID{tls.X25519MLKEM768, tls.X25519, tls.CurveP256},
		SessionTicketKey: sessionTicketKey,
	}

	hrrTLS := &tls.Config{
		Certificates:           []tls.Certificate{cert},
		NextProtos:             []string{"h2", "http/1.1"},
		MinVersion:             tls.VersionTLS13,
		MaxVersion:             tls.VersionTLS13,
		CurvePreferences:       []tls.CurveID{tls.CurveP256},
		SessionTicketsDisabled: true,
	}

	quicTLS := &tls.Config{
		Certificates:           []tls.Certificate{cert},
		NextProtos:             []string{"h3"},
		MinVersion:             tls.VersionTLS13,
		MaxVersion:             tls.VersionTLS13,
		CurvePreferences:       []tls.CurveID{tls.X25519MLKEM768, tls.X25519, tls.CurveP256},
		SessionTicketsDisabled: false,
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	tcpLn, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		fmt.Fprintf(os.Stderr, "tcp listen failed: %v\n", err)
		os.Exit(1)
	}
	go serveTCPListener(ctx, tcpLn, mainTLS, "tcp-h2")

	hrrLn, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		fmt.Fprintf(os.Stderr, "hrr listen failed: %v\n", err)
		os.Exit(1)
	}
	go serveTCPListener(ctx, hrrLn, hrrTLS, "hrr-p256")

	udpPC, err := net.ListenPacket("udp", "127.0.0.1:0")
	if err != nil {
		fmt.Fprintf(os.Stderr, "udp listen failed: %v\n", err)
		os.Exit(1)
	}
	if _, err := startH3Server(ctx, udpPC, quicTLS, "quic-h3", false); err != nil {
		fmt.Fprintf(os.Stderr, "h3 start failed: %v\n", err)
		os.Exit(1)
	}

	retryPC, err := net.ListenPacket("udp", "127.0.0.1:0")
	if err != nil {
		fmt.Fprintf(os.Stderr, "retry udp listen failed: %v\n", err)
		os.Exit(1)
	}
	if _, err := startH3Server(ctx, retryPC, quicTLS, "quic-retry-h3", true); err != nil {
		fmt.Fprintf(os.Stderr, "retry h3 start failed: %v\n", err)
		os.Exit(1)
	}

	dualTCP, dualUDP, dualAddr, err := bindDualPort()
	if err != nil {
		fmt.Fprintf(os.Stderr, "dual bind failed: %v\n", err)
		os.Exit(1)
	}
	go serveTCPListener(ctx, dualTCP, mainTLS, "dual-tcp")
	if _, err := startH3Server(ctx, dualUDP, quicTLS, "dual-h3", false); err != nil {
		fmt.Fprintf(os.Stderr, "dual h3 start failed: %v\n", err)
		os.Exit(1)
	}

	bhTCP, bhUDP, blackholeAddr, err := bindDualPort()
	if err != nil {
		fmt.Fprintf(os.Stderr, "blackhole bind failed: %v\n", err)
		os.Exit(1)
	}
	go serveTCPListener(ctx, bhTCP, mainTLS, "blackhole-fallback-tcp")
	var droppedUDP atomic.Int64
	go func() {
		buf := make([]byte, 4096)
		for {
			if _, _, err := bhUDP.ReadFrom(buf); err != nil {
				return
			}
			droppedUDP.Add(1)
		}
	}()

	ready := struct {
		TcpAddr       string `json:"tcpAddr"`
		HrrAddr       string `json:"hrrAddr"`
		UdpAddr       string `json:"udpAddr"`
		RetryUdpAddr  string `json:"retryUdpAddr"`
		DualAddr      string `json:"dualAddr"`
		BlackholeAddr string `json:"blackholeAddr"`
	}{
		TcpAddr:       tcpLn.Addr().String(),
		HrrAddr:       hrrLn.Addr().String(),
		UdpAddr:       udpPC.LocalAddr().String(),
		RetryUdpAddr:  retryPC.LocalAddr().String(),
		DualAddr:      dualAddr,
		BlackholeAddr: blackholeAddr,
	}
	line, _ := json.Marshal(ready)
	fmt.Println(string(strings.TrimSpace(string(line))))

	<-ctx.Done()
	_ = tcpLn.Close()
	_ = hrrLn.Close()
	_ = dualTCP.Close()
	_ = bhTCP.Close()
	_ = bhUDP.Close()
}
