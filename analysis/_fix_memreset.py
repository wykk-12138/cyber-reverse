import io
p = r'D:\projects\cyber-reverse\analysis\memreset.ps1'
t = io.open(p, encoding='utf-8').read()

# 1) reuse the known-good struct/call (the ad-hoc one returned zeros because the struct lacked cb and layout)
old_struct_start = t.index('    [StructLayout(LayoutKind.Sequential)]\n    public struct PERFINFO {')
old_struct_end = t.index('    [DllImport("psapi.dll", SetLastError = true)]\n    public static extern bool GetPerformanceInfo')
new_struct = '''    [StructLayout(LayoutKind.Sequential)]
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

'''
t = t[:old_struct_start] + new_struct + t[old_struct_end:]

t = t.replace('    public static extern bool GetPerformanceInfo(out PERFINFO info, int size);',
              '    public static extern bool GetPerformanceInfo(out PERFINFO info, uint size);')

# 2) fix Snapshot to use the right size and print properly
old_snap_start = t.index('function Snapshot([string]$when) {')
old_snap_end = t.index('$admin = ([Security.Principal.WindowsPrincipal]')
new_snap = '''function Snapshot([string]$when) {
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

'''
t = t[:old_snap_start] + new_snap + t[old_snap_end:]

# 3) fix the two status lines that swallowed the format
t = t.replace('W "   status 0x{0:X8} {1}" -f $s1, $(if ($s1 -eq 0) { \'ok\' } else { \'refused\' })',
              'W ("   status 0x{0:X8} {1}" -f $s1, $(if ($s1 -eq 0) { \'ok\' } else { \'refused\' }))')
t = t.replace('W "   status 0x{0:X8} {1}" -f $s2, $(if ($s2 -eq 0) { \'ok\' } else { \'refused\' })',
              'W ("   status 0x{0:X8} {1}" -f $s2, $(if ($s2 -eq 0) { \'ok\' } else { \'refused\' }))')

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('memreset.ps1 fixed')
