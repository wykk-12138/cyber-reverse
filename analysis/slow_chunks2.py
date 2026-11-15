import io
import re
import subprocess
import sys

DOTNET = r"D:\tools\dotnet8\dotnet.exe"
PROJ = r"tests\Cybersole.Tests\Cybersole.Tests.csproj"
CWD = r"C:\Users\wykk\AppData\Local\Cybersole\replica"

CHUNKS = [
    ["NonParityClaimsTests", "OwnTlsFallbackTests", "KasadaHeaderSurfaceTests"],
    ["NikeKasadaFlowTests", "KasadaIntrospectionTests", "KasadaLiveTests"],
    ["LiveContractTests", "LiveBrowserProbeTests", "ChromiumBridgeTests", "ChromiumStealthTests"],
    ["ModuleReachabilityTests", "ModuleRobustnessTests", "AllFlowsMonitorTests"],
    ["ShopifyWrappingTests", "MagentoWrappingTests", "DemandwareAndFootsitesTests"],
    ["HybrisCartPathTests", "SupremePlatformTests", "OffspringPlatformTests", "HbxPlatformTests"],
    ["WarhammerEndpointTests", "WarhammerHostTests", "JbHiFiPlatformTests", "CasioEndpointTests"],
    ["FirstDomainResolvesTests", "PlatformEvidenceTests", "TransportParityProbeTests"],
    ["ProductPageProbeTests", "RealPageParserTests", "IdentifierFieldProbeTests",
     "SizeFieldProbeTests", "PageKeyProbeTests", "InterfaceInventoryTests"],
    ["PerformanceTests", "TlsTransportPerformanceTests"],
]


def run(chunk):
    expr = "|".join("FullyQualifiedName~" + name for name in chunk)
    out = subprocess.run(
        [DOTNET, "test", PROJ, "--filter", expr, "-v", "q", "--nologo"],
        capture_output=True, cwd=CWD, timeout=300)
    # decode defensively: the console code page is GBK here and console output is mixed
    text = (out.stdout or b"").decode("utf-8", "replace") + (out.stderr or b"").decode("utf-8", "replace")
    passed = re.search(r"通过:\s*(\d+)", text) or re.search(r"Passed:\s*(\d+)", text)
    failed = re.search(r"失败:\s*(\d+)", text) or re.search(r"Failed:\s*(\d+)", text)
    fails = [l.strip() for l in text.splitlines() if "[FAIL]" in l or l.strip().startswith("失败 ")]
    return out.returncode, (passed.group(1) if passed else "?"), (failed.group(1) if failed else "?"), fails[:3]


total_pass = total_fail = 0
bad = []

for i, chunk in enumerate(CHUNKS, 1):
    try:
        code, p, f, fails = run(chunk)
    except subprocess.TimeoutExpired:
        print("TIMEOUT chunk %2d  %s" % (i, ", ".join(chunk)[:60]))
        total_fail += 1
        continue

    total_pass += int(p) if p.isdigit() else 0
    total_fail += int(f) if f.isdigit() else 0
    flag = "OK  " if code == 0 else "FAIL"
    print("%s chunk %2d  passed=%-4s failed=%-3s  %s" % (flag, i, p, f, ", ".join(chunk)[:66]))
    if code != 0:
        bad.extend(fails)

print()
print("TOTAL passed=%d failed=%d" % (total_pass, total_fail))
for line in bad:
    print("   ", line[:150])
