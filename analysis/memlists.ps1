param()
$source = @'
using System;
using System.Runtime.InteropServices;

public static class MemLists
{
    [DllImport("ntdll.dll")]
    public static extern int NtQuerySystemInformation(int infoClass, IntPtr buffer, int length, out int returned);

    public static string Report()
    {
        // SystemMemoryListInformation = 0x50, fifteen SIZE_T fields on x64
        int size = 40 * IntPtr.Size;
        IntPtr buf = Marshal.AllocHGlobal(size);
        try
        {
            int returned;
            int status = NtQuerySystemInformation(0x50, buf, size, out returned);
            if (status != 0) return "NtQuerySystemInformation failed: 0x" + status.ToString("X8") + " returned=" + returned;

            long[] v = new long[40];
            for (int i = 0; i < 40; i++) v[i] = Marshal.ReadInt64(buf, i * IntPtr.Size);

            const double KB = 4.0;                    // one 4 KB page, in KB
            Func<long, double> gb = pages => Math.Round(pages * KB / 1048576.0, 2);

            long standby = 0;
            for (int i = 5; i < 13; i++) standby += v[i];

            return string.Format(
                "Zero      {0,7} GB\nFree      {1,7} GB\nModified  {2,7} GB\nModNoWrite{3,7} GB\nBad       {4,7} GB\n" +
                "Standby   {5,7} GB  (sum of 8 priorities)\nRepurposed{6,7} GB\nModifiedInPageFile {7} GB\n" +
                "SUM(free+zero+modified+standby) {8} GB",
                gb(v[0]), gb(v[1]), gb(v[2]), gb(v[3]), gb(v[4]),
                gb(standby), gb(v[13]), gb(v[14]),
                gb(v[0] + v[1] + v[2] + v[3] + standby));
        }
        finally { Marshal.FreeHGlobal(buf); }
    }
}
'@

Add-Type -TypeDefinition $source -Language CSharp
[MemLists]::Report()
