Add-Type -TypeDefinition @"\nusing System;
using System.Runtime.InteropServices;
public static class PerfInfo {
    [StructLayout(LayoutKind.Sequential)]
    public struct PERFORMANCE_INFORMATION {
        public uint cb;
        public IntPtr CommitTotal, CommitLimit, CommitPeak, PhysicalTotal, PhysicalAvailable;
        public IntPtr SystemCache, KernelTotal, KernelPaged, KernelNonpaged, PageSize;
        public uint HandleCount, ProcessCount, ThreadCount;
    }
    [DllImport("psapi.dll", SetLastError = true)]
    public static extern bool GetPerformanceInfo(out PERFORMANCE_INFORMATION p, uint cb);
    public static string Report() {
        PERFORMANCE_INFORMATION p;
        if (!GetPerformanceInfo(out p, (uint)Marshal.SizeOf(typeof(PERFORMANCE_INFORMATION))))
            return "call failed: " + Marshal.GetLastWin32Error();
        double pg = p.PageSize.ToInt64() / 1048576.0;   // MB per page
        Func<IntPtr, double> gb = v => Math.Round(v.ToInt64() * pg / 1024.0, 2);
        return string.Format(
            "Commit {0} / {1} GB (peak {2})\nPhysical total {3} GB  available {4} GB\n" +
            "SystemCache {5} GB\nKernelTotal {6} GB  =  nonpaged {7} + paged {8}\n" +
            "handles {9}  processes {10}  threads {11}",
            gb(p.CommitTotal), gb(p.CommitLimit), gb(p.CommitPeak),
            gb(p.PhysicalTotal), gb(p.PhysicalAvailable), gb(p.SystemCache),
            gb(p.KernelTotal), gb(p.KernelNonpaged), gb(p.KernelPaged),
            p.HandleCount, p.ProcessCount, p.ThreadCount);
    }
}
"@ -Language CSharp; [PerfInfo]::Report()
