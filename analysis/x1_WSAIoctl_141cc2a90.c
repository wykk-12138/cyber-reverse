/* x1 WSAIoctl via cref @ 0x141cc2a90 */
__int64 __fastcall sub_141CC2A90(
        __int64 a1,
        DWORD dwIoControlCode,
        __int64 a3,
        DWORD cbInBuffer,
        __int64 a5,
        DWORD cbOutBuffer,
        DWORD *lpcbBytesReturned,
        struct _OVERLAPPED *lpOverlapped,
        void (__stdcall *lpCompletionRoutine)(DWORD dwError, DWORD cbTransferred, LPWSAOVERLAPPED lpOverlapped, DWORD dwFlags))
{
  void *lpvOutBuffer; // r13
  void *lpvInBuffer; // r15
  SOCKET s; // rbx
  unsigned int v15; // ebx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v18; // rdi
  _BYTE v20[40]; // [rsp+68h] [rbp-90h] BYREF
  __int128 v21; // [rsp+90h] [rbp-68h]
  DWORD *lpcbBytesReturned_1; // [rsp+A0h] [rbp-58h]
  __int128 v23; // [rsp+A8h] [rbp-50h] BYREF

  v21 = 0;
  *lpcbBytesReturned = 0;
  v23 = 0;
  *(_QWORD *)&v23 = a1;
  sub_141DC71A0(a1, (char *)&v23 + 8);
  lpcbBytesReturned_1 = lpcbBytesReturned;
  lpvOutBuffer = (void *)(a5 + 16);
  if ( !a5 )
    lpvOutBuffer = nullptr;
  *((_QWORD *)&v21 + 1) = lpvOutBuffer;
  lpvInBuffer = (void *)(a3 + 16);
  if ( !a3 )
    lpvInBuffer = nullptr;
  *(_QWORD *)&v21 = lpvInBuffer;
  s = *(_QWORD *)(v23 + 8);
  SetLastError(0);
  sub_14301AE60(v20);
  v15 = WSAIoctl(
          s,
          dwIoControlCode,
          lpvInBuffer,
          cbInBuffer,
          lpvOutBuffer,
          cbOutBuffer,
          lpcbBytesReturned,
          lpOverlapped,
          lpCompletionRoutine);
  sub_14301AEB0(v20);
  LastError = GetLastError();
  v21 = 0u;
  lpcbBytesReturned_1 = nullptr;
  if ( BYTE8(v23) )
    sub_141DC7200(v23, 0);
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v18 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v18 )
    v18 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v18 + 424) = LastError;
  return v15;
}
