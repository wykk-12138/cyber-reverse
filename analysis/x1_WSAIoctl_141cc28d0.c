/* x1 WSAIoctl via cref @ 0x141cc28d0 */
__int64 __fastcall sub_141CC28D0(
        __int64 a1,
        DWORD dwIoControlCode,
        void *lpvInBuffer,
        DWORD cbInBuffer,
        _QWORD *lpvOutBuffer,
        DWORD cbOutBuffer,
        DWORD *lpcbBytesReturned,
        struct _OVERLAPPED *lpOverlapped,
        void (__stdcall *lpCompletionRoutine)(DWORD dwError, DWORD cbTransferred, LPWSAOVERLAPPED lpOverlapped, DWORD dwFlags))
{
  SOCKET s; // r13
  unsigned int v13; // ebx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v16; // rdi
  _BYTE v18[40]; // [rsp+68h] [rbp-90h] BYREF
  void *lpvInBuffer_1; // [rsp+90h] [rbp-68h]
  _QWORD *lpvOutBuffer_1; // [rsp+98h] [rbp-60h]
  DWORD *lpcbBytesReturned_1; // [rsp+A0h] [rbp-58h]
  __int128 v22; // [rsp+A8h] [rbp-50h] BYREF

  *lpvOutBuffer = 0;
  *lpcbBytesReturned = 0;
  v22 = 0;
  *(_QWORD *)&v22 = a1;
  sub_141DC71A0(a1, (char *)&v22 + 8);
  lpcbBytesReturned_1 = lpcbBytesReturned;
  lpvOutBuffer_1 = lpvOutBuffer;
  lpvInBuffer_1 = lpvInBuffer;
  s = *(_QWORD *)(v22 + 8);
  SetLastError(0);
  sub_14301AE60(v18);
  v13 = WSAIoctl(
          s,
          dwIoControlCode,
          lpvInBuffer,
          cbInBuffer,
          lpvOutBuffer,
          cbOutBuffer,
          lpcbBytesReturned,
          lpOverlapped,
          lpCompletionRoutine);
  sub_14301AEB0(v18);
  LastError = GetLastError();
  lpvInBuffer_1 = nullptr;
  lpvOutBuffer_1 = nullptr;
  lpcbBytesReturned_1 = nullptr;
  if ( BYTE8(v22) )
    sub_141DC7200(v22, 0);
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v16 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v16 )
    v16 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v16 + 424) = LastError;
  return v13;
}
