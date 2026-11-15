param(
    [switch]$MeasureOnly,
    [string]$Log = 'D:\projects\cyber-reverse\analysis\memreset.log'
)

$ErrorActionPreference = 'Continue'

function W([string]$m) {
    $line = "[{0:HH:mm:ss}] {1}" -f (Get-Date), $m
    Write-Host $line
    Add-Content -Path $Log -Value $line -Encoding UTF8
}

Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class Mem {
    [DllImport("ntdll.dll")]
    public static extern int NtSetSystemInformation(int InfoClass, IntPtr Info, int Length);

    [DllImport("ntdll.dll")]
    public static extern int NtQuerySystemInformation(int InfoClass, IntPtr Info, int Length, out int ReturnLength);

    [DllImport("psapi.dll")]
    public static extern int EmptyWorkingSet(IntPtr hProcess);

    [DllImport("kernel32.dll")]
    public static extern IntPtr OpenProcess(uint access, bool inherit, int pid);

    [DllImport("kernel32.dll")]
    public static extern bool CloseHandle(IntPtr h);

    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool OpenProcessToken(IntPtr h, uint access, out IntPtr token);

    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool LookupPrivilegeValue(string system, string name, out long luid);

    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool AdjustTokenPrivileges(IntPtr token, bool disableAll, ref TOKEN_PRIVILEGES newState,
        int len, IntPtr prev, IntPtr retLen);

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct TOKEN_PRIVILEGES {
        public int Count;
        public long Luid;
        public int Attributes;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct PERFINFO {
        public uint cb;
        public IntPtr CommitTotal;
        public IntPtr CommitLimit;
        public IntPtr CommitPeak;
        public IntPtr PhysicalTotal;
        public IntPtr PhysicalAvailable;
        public IntPtr SystemCache;
        public IntPtr KernelTotal;
        public IntPtr KernelPaged;
        public IntPtr KernelNonpaged;
        public IntPtr PageSize;
        public uint HandleCount;
        public uint ProcessCount;
        public uint ThreadCount;
    }

    [DllImport("psapi.dll", SetLastError = true)]
    public static extern bool GetPerformanceInfo(out PERFINFO info, uint size);

    // command 4 = MemoryPurgeStandbyList, 5 = MemoryPurgeLowPriorityStandbyList
    public static int Purge(int command) {
        IntPtr p = Marshal.AllocHGlobal(sizeof(int));
        Marshal.WriteInt32(p, command);
        int status = NtSetSystemInformation(0x50, p, sizeof(int));
        Marshal.FreeHGlobal(p);
        return status;
    }

    public static bool EnablePrivilege(string name) {
        IntPtr token;
        if (!OpenProcessToken(OpenProcess(0x0020 | 0x0008, false,
                System.Diagnostics.Process.GetCurrentProcess().Id), 0x0020 | 0x0008, out token))
            return false;
        long luid;
        if (!LookupPrivilegeValue(null, name, out luid)) return false;
        var tp = new TOKEN_PRIVILEGES { Count = 1, Luid = luid, Attributes = 0x00000002 };
        bool ok = AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
        CloseHandle(token);
        return ok;
    }
}
"@ | Out-Null

function Snapshot([string]$when) {
    $i = New-Object Mem+PERFINFO
    if (-not [Mem]::GetPerformanceInfo([ref]$i, [uint32][System.Runtime.InteropServices.Marshal]::SizeOf([type]([Mem+PERFINFO])))) {
        W "  GetPerformanceInfo failed"
        return [pscustomobject]@{ CommitGB = 0; AvailGB = 0 }
    }
    $pageMB = [double]$i.PageSize.ToInt64() / 1MB
    $commitGB = [Math]::Round([double]$i.CommitTotal.ToInt64() * $pageMB / 1024, 2)
    $limitGB = [Math]::Round([double]$i.CommitLimit.ToInt64() * $pageMB / 1024, 2)
    $availGB = [Math]::Round([double]$i.PhysicalAvailable.ToInt64() * $pageMB / 1024, 2)
    $cacheGB = [Math]::Round([double]$i.SystemCache.ToInt64() * $pageMB / 1024, 2)
    W ("{0,-8} Commit {1,6} / {2,6} GB   available {3,5} GB   cache {4,5} GB" -f $when, $commitGB, $limitGB, $availGB, $cacheGB)
    return [pscustomobject]@{ CommitGB = $commitGB; AvailGB = $availGB }
}

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)

Set-Content -Path $Log -Value "# memreset $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  elevated=$admin" -Encoding UTF8

$before = Snapshot 'before'

if ($MeasureOnly) {
    W 'measure only — nothing changed'
    return
}

if (-not $admin) {
    W 'ABORT: purging standby lists needs SeProfileSingleProcessPrivilege (administrator)'
    return
}

[Mem]::EnablePrivilege('SeProfileSingleProcessPrivilege') | Out-Null
[Mem]::EnablePrivilege('SeIncreaseQuotaPrivilege') | Out-Null

W '-- empty every process working set --'
$ok = 0
foreach ($p in Get-Process -ErrorAction SilentlyContinue) {
    try {
        $h = [Mem]::OpenProcess(0x0100 -bor 0x0400, $false, $p.Id)
        if ($h -ne [IntPtr]::Zero) {
            if ([Mem]::EmptyWorkingSet($h) -ne 0) { $ok++ }
            [Mem]::CloseHandle($h) | Out-Null
        }
    } catch { }
}
W "   trimmed $ok processes"

W '-- purge standby list (command 4) --'
$s1 = [Mem]::Purge(4)
W ("   status 0x{0:X8} {1}" -f $s1, $(if ($s1 -eq 0) { 'ok' } else { 'refused' }))

W '-- purge low-priority standby list (command 5) --'
$s2 = [Mem]::Purge(5)
W ("   status 0x{0:X8} {1}" -f $s2, $(if ($s2 -eq 0) { 'ok' } else { 'refused' }))

Start-Sleep -Seconds 3
$after = Snapshot 'after'

W ("delta: commit {0:+0.00;-0.00;0.00} GB   available {1:+0.00;-0.00;0.00} GB" -f
    ($after.CommitGB - $before.CommitGB), ($after.AvailGB - $before.AvailGB))
