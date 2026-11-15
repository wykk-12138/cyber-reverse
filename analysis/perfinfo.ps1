param()
$source = @'
using System;
using System.Runtime.InteropServices;

public static class PerfInfo
{
    [StructLayout(LayoutKind.Sequential)]
    public struct PERFORMANCE_INFORMATION
    {
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
    public static extern bool GetPerformanceInfo(out PERFORMANCE_INFORMATION p, uint cb);

    public static string Report()
    {
        PERFORMANCE_INFORMATION p;
        if (!GetPerformanceInfo(out p, (uint)Marshal.SizeOf(typeof(PERFORMANCE_INFORMATION))))
            return "GetPerformanceInfo failed: " + Marshal.GetLastWin32Error();

        double pageMb = p.PageSize.ToInt64() / 1048576.0;
        Func<long, double> gb = v => Math.Round(v * pageMb / 1024.0, 2);

        return string.Format(
            "Commit        {0} / {1} GB  (peak {2})\n" +
            "Physical      total {3} GB   available {4} GB\n" +
            "SystemCache   {5} GB\n" +
            "KernelTotal   {6} GB  =  nonpaged {7} + paged {8}\n" +
            "handles {9}  processes {10}  threads {11}",
            gb(p.CommitTotal.ToInt64()), gb(p.CommitLimit.ToInt64()), gb(p.CommitPeak.ToInt64()),
            gb(p.PhysicalTotal.ToInt64()), gb(p.PhysicalAvailable.ToInt64()),
            gb(p.SystemCache.ToInt64()),
            gb(p.KernelTotal.ToInt64()), gb(p.KernelNonpaged.ToInt64()), gb(p.KernelPaged.ToInt64()),
            p.HandleCount, p.ProcessCount, p.ThreadCount);
    }
}
'@

Add-Type -TypeDefinition $source -Language CSharp
[PerfInfo]::Report()
