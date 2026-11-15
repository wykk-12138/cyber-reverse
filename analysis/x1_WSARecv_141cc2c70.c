/* x1 WSARecv via cref @ 0x141cc2c70 */
__int64 __fastcall sub_141CC2C70(
        __int64 a1,
        struct _WSABUF *lpBuffers,
        DWORD dwBufferCount,
        DWORD *lpNumberOfBytesRecvd,
        DWORD *lpFlags,
        struct _OVERLAPPED *lpOverlapped,
        void (__stdcall *lpCompletionRoutine)(DWORD dwError, DWORD cbTransferred, LPWSAOVERLAPPED lpOverlapped, DWORD dwFlags))
{
  SOCKET s; // r15
  unsigned int v11; // ebx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v14; // rdi
  _BYTE v16[40]; // [rsp+60h] [rbp-88h] BYREF
  DWORD *lpNumberOfBytesRecvd_1; // [rsp+88h] [rbp-60h]
  DWORD *lpFlags_1; // [rsp+90h] [rbp-58h]
  __int128 v19; // [rsp+98h] [rbp-50h] BYREF

  *lpNumberOfBytesRecvd = 0;
  v19 = 0;
  *(_QWORD *)&v19 = a1;
  sub_141DC71A0(a1, (char *)&v19 + 8);
  lpFlags_1 = lpFlags;
  lpNumberOfBytesRecvd_1 = lpNumberOfBytesRecvd;
  s = *(_QWORD *)(v19 + 8);
  SetLastError(0);
  sub_14301AE60(v16);
  v11 = WSARecv(s, lpBuffers, dwBufferCount, lpNumberOfBytesRecvd, lpFlags, lpOverlapped, lpCompletionRoutine);
  sub_14301AEB0(v16);
  LastError = GetLastError();
  lpNumberOfBytesRecvd_1 = nullptr;
  lpFlags_1 = nullptr;
  if ( BYTE8(v19) )
    sub_141DC7200(v19, 0);
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v14 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v14 )
    v14 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v14 + 424) = LastError;
  return v11;
}
