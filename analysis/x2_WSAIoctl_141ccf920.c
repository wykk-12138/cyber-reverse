/* x2 WSAIoctl via cref @ 0x141ccf920 */
__int64 __fastcall sub_141CCF920(__int64 a1, DWORD dwIoControlCode, __int64 a3, __int64 a4, DWORD *lpcbBytesReturned)
{
  DWORD cbInBuffer; // eax
  DWORD cbOutBuffer; // r10d
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v8; // rbx
  __int64 v10; // rbx

  if ( dwIoControlCode == -2147195266 )
  {
    v10 = sub_143019310(&unk_144DA6B00);
    sub_141D18B00(v10, &off_146EFC188);
    sub_1430198D0(v10);
    __debugbreak();
  }
  if ( a3 )
    cbInBuffer = *(_DWORD *)(a3 + 8);
  else
    cbInBuffer = 0;
  if ( a4 )
    cbOutBuffer = *(_DWORD *)(a4 + 8);
  else
    cbOutBuffer = 0;
  if ( (unsigned int)sub_141CC2A90(
                       a1,
                       dwIoControlCode,
                       a3,
                       cbInBuffer,
                       a4,
                       cbOutBuffer,
                       lpcbBytesReturned,
                       nullptr,
                       nullptr) != -1 )
    return 0;
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v8 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v8 )
    v8 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  return *(unsigned int *)(v8 + 424);
}
