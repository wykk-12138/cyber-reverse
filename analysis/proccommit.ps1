param()
$source = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class ProcCommit
{
    [DllImport("ntdll.dll")]
    static extern int NtQuerySystemInformation(int cls, IntPtr buf, int len, out int ret);

    // SYSTEM_PROCESS_INFORMATION, x64 layout.  Only the fields needed here are read, by offset.
    //  0 NextEntryOffset(4) 4 NumberOfThreads(4) 8/16 WorkingSetPrivate-ish fields...
    // Offsets used: 0x38 PagefileUsage(8)  0x40 PrivatePageCount(8)  0x78 ImageName (UNICODE_STRING)
    public static string Report()
    {
        int len = 1 << 22;
        IntPtr buf = Marshal.AllocHGlobal(len);
        try
        {
            int ret;
            int st = NtQuerySystemInformation(0x05, buf, len, out ret);   // SystemProcessInformation
            if (st != 0) return "status 0x" + st.ToString("X8");

            long totalCommit = 0, totalWs = 0;
            int count = 0;
            var top = new List<Tuple<long, string>>();
            int off = 0;
            while (true)
            {
                IntPtr p = (IntPtr)(buf.ToInt64() + off);
                int next = Marshal.ReadInt32(p, 0);
                long pagefile = Marshal.ReadInt64(p, 0xB8);   // PagefileUsage
                long ppc = Marshal.ReadInt64(p, 0xC8);       // PrivatePageCount

                int nameLen = Marshal.ReadInt16(p, 0x38);   // ImageName.Length
                string name = "";
                if (nameLen > 0)
                {
                    IntPtr strPtr = Marshal.ReadIntPtr(p, 0x40); // ImageName.Buffer
                    if (strPtr != IntPtr.Zero && nameLen < 512)
                        name = Marshal.PtrToStringUni(strPtr, Math.Min(nameLen / 2, 60));
                }

                totalCommit += pagefile;
                totalWs += ppc;
                if (pagefile > 0) top.Add(Tuple.Create(pagefile, name));
                count++;

                if (next == 0) break;
                off += next;
                if (off >= len) break;
            }

            top.Sort((a, b) => b.Item1.CompareTo(a.Item1));
            var sb = new System.Text.StringBuilder();
            sb.AppendLine("processes " + count);
            sb.AppendLine("sum PagefileUsage (commit)  " + Math.Round(totalCommit / 1048576.0, 2) + " GB");
            sb.AppendLine("sum PrivatePageCount (ws)   " + Math.Round(totalWs / 1048576.0, 2) + " GB");
            sb.AppendLine("--- top 10 by commit ---");
            for (int i = 0; i < Math.Min(10, top.Count); i++)
                sb.AppendLine(string.Format("  {0,-28} {1,7} MB", top[i].Item2, top[i].Item1 / 1048576));
            return sb.ToString();
        }
        finally { Marshal.FreeHGlobal(buf); }
    }
}
'@

Add-Type -TypeDefinition $source -Language CSharp
[ProcCommit]::Report()
