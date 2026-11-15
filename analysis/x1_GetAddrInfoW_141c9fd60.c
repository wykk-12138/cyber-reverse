/* x1 GetAddrInfoW via cref @ 0x141c9fd60 */
__int64 __fastcall sub_141C9FD60(__int64 a1, __int64 a2, const ADDRINFOW *pHints, PADDRINFOW *ppResult)
{
  const WCHAR *pServiceName; // rdi
  const WCHAR *pNodeName; // r14
  unsigned int AddrInfoW; // ebx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v11; // rdi
  _BYTE v13[40]; // [rsp+40h] [rbp-78h] BYREF
  const WCHAR *pNodeName_1; // [rsp+68h] [rbp-50h]
  const WCHAR *pServiceName_1; // [rsp+70h] [rbp-48h]

  pServiceName_1 = nullptr;
  pNodeName_1 = nullptr;
  if ( a2 )
    pServiceName = (const WCHAR *)(a2 + 12);
  else
    pServiceName = nullptr;
  pServiceName_1 = pServiceName;
  if ( a1 )
    pNodeName = (const WCHAR *)(a1 + 12);
  else
    pNodeName = nullptr;
  pNodeName_1 = pNodeName;
  SetLastError(0);
  sub_14301AE60(v13);
  AddrInfoW = GetAddrInfoW(pNodeName, pServiceName, pHints, ppResult);
  sub_14301AEB0(v13);
  LastError = GetLastError();
  pNodeName_1 = nullptr;
  pServiceName_1 = nullptr;
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v11 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v11 )
    v11 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v11 + 424) = LastError;
  return AddrInfoW;
}
