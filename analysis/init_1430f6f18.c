__int64 sub_1430F6F18()
{
  uintptr_t __security_cookie; // rax
  __int64 result; // rax
  struct _FILETIME SystemTimeAsFileTime_1; // [rsp+20h] [rbp-10h] BYREF
  struct _FILETIME SystemTimeAsFileTime; // [rsp+40h] [rbp+10h] BYREF
  LARGE_INTEGER PerformanceCount; // [rsp+48h] [rbp+18h] BYREF

  __security_cookie = _security_cookie;
  if ( _security_cookie == 0x2B992DDFA232LL )
  {
    SystemTimeAsFileTime = 0;
    GetSystemTimeAsFileTime(&SystemTimeAsFileTime);
    SystemTimeAsFileTime_1 = SystemTimeAsFileTime;
    SystemTimeAsFileTime_1 = (struct _FILETIME)(GetCurrentThreadId() ^ *(unsigned __int64 *)&SystemTimeAsFileTime_1);
    SystemTimeAsFileTime_1 = (struct _FILETIME)(GetCurrentProcessId() ^ *(unsigned __int64 *)&SystemTimeAsFileTime_1);
    QueryPerformanceCounter(&PerformanceCount);
    __security_cookie = ((unsigned __int64)&SystemTimeAsFileTime_1
                       ^ *(_QWORD *)&SystemTimeAsFileTime_1
                       ^ PerformanceCount.QuadPart
                       ^ ((unsigned __int64)PerformanceCount.LowPart << 32))
                      & 0xFFFFFFFFFFFFLL;
    if ( __security_cookie == 0x2B992DDFA232LL )
      __security_cookie = 0x2B992DDFA233LL;
    _security_cookie = __security_cookie;
  }
  result = ~__security_cookie;
  qword_1473E9B40 = result;
  return result;
}
