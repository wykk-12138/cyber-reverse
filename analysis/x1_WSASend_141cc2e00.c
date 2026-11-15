/* x1 WSASend via cref @ 0x141cc2e00 */
__int64 __fastcall sub_141CC2E00(
        __int64 a1,
        struct _WSABUF *lpBuffers,
        DWORD dwBufferCount,
        DWORD *lpNumberOfBytesSent,
        DWORD dwFlags,
        struct _OVERLAPPED *lpOverlapped,
        void (__stdcall *lpCompletionRoutine)(DWORD dwError, DWORD cbTransferred, LPWSAOVERLAPPED lpOverlapped, DWORD dwFlags))
{
  SOCKET s; // r14
  unsigned int v11; // ebx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v14; // rdi
  _BYTE v16[40]; // [rsp+58h] [rbp-80h] BYREF
  DWORD *lpNumberOfBytesSent_1; // [rsp+80h] [rbp-58h]
  __int128 v18; // [rsp+88h] [rbp-50h] BYREF

  *lpNumberOfBytesSent = 0;
  v18 = 0;
  *(_QWORD *)&v18 = a1;
  sub_141DC71A0(a1, (char *)&v18 + 8);
  lpNumberOfBytesSent_1 = lpNumberOfBytesSent;
  s = *(_QWORD *)(v18 + 8);
  SetLastError(0);
  sub_14301AE60(v16);
  v11 = WSASend(s, lpBuffers, dwBufferCount, lpNumberOfBytesSent, dwFlags, lpOverlapped, lpCompletionRoutine);
  sub_14301AEB0(v16);
  LastError = GetLastError();
  lpNumberOfBytesSent_1 = nullptr;
  if ( BYTE8(v18) )
    sub_141DC7200(v18, 0);
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v14 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v14 )
    v14 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v14 + 424) = LastError;
  return v11;
}
