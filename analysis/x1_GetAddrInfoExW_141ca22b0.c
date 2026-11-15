/* x1 GetAddrInfoExW via cref @ 0x141ca22b0 */
__int64 __fastcall sub_141CA22B0(__int64 a1, unsigned __int8 a2, int ai_family, __int64 a4)
{
  __int64 v7; // r15
  __int64 lpOverlapped; // rsi
  const WCHAR *pName; // r12
  unsigned int AddrInfo; // ebx
  WINERROR LastError; // edi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v13; // r14
  _BYTE v15[40]; // [rsp+80h] [rbp-B8h] BYREF
  const WCHAR *pName_1; // [rsp+A8h] [rbp-90h]
  ADDRINFOEXW hints; // [rsp+B0h] [rbp-88h] BYREF

  pName_1 = nullptr;
  if ( !dword_1473E9DA4 )
    sub_141C9FF60();
  v7 = sub_143019350(&unk_144D9D4D8);
  sub_141CA2C00(v7, a1, a2);
  memset(&hints, 0, sizeof(hints));
  hints.ai_family = ai_family;
  if ( !a2 )
    hints.ai_flags = 2;
  lpOverlapped = *(_QWORD *)(v7 + 8);
  if ( a1 )
    pName = (const WCHAR *)(a1 + 12);
  else
    pName = nullptr;
  pName_1 = pName;
  SetLastError(0);
  sub_14301AE60(v15);
  AddrInfo = GetAddrInfoExW(
               pName,
               nullptr,
               0,
               nullptr,
               &hints,
               (PADDRINFOEXW *)(lpOverlapped + 32),
               nullptr,
               (LPOVERLAPPED)lpOverlapped,
               CompletionRoutine,
               (LPHANDLE)(lpOverlapped + 40));
  sub_14301AEB0(v15);
  LastError = GetLastError();
  pName_1 = nullptr;
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v13 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v13 )
    v13 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v13 + 424) = LastError;
  if ( AddrInfo == 997 )
  {
    sub_141CA2D50(v7, a4);
  }
  else
  {
    if ( AddrInfo == 11002 || AddrInfo == 10111 )
    {
      sub_141DC7200(v7, 1);
      sub_141CE7170(v7);
      return 0;
    }
    sub_141CA2530(AddrInfo, lpOverlapped);
  }
  return sub_141CA2D10(v7);
}
