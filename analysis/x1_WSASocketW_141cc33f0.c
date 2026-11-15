/* x1 WSASocketW via cref @ 0x141cc33f0 */
_BOOL8 __fastcall sub_141CC33F0(int a1)
{
  SOCKET v2; // rbx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v5; // rdi
  bool v6; // si
  _BYTE v8[40]; // [rsp+50h] [rbp-78h] BYREF
  __int64 v9; // [rsp+78h] [rbp-50h]
  __int64 v10; // [rsp+80h] [rbp-48h]

  if ( !dword_1473E9DB0 )
    sub_141CC2F70();
  v10 = -1;
  v9 = -1;
  SetLastError(0);
  sub_14301AE60(v8);
  v2 = WSASocketW(a1, 1, 0, nullptr, 0, 0x80u);
  sub_14301AEB0(v8);
  LastError = GetLastError();
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v5 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v5 )
    v5 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v5 + 424) = LastError;
  v9 = v2;
  v6 = v2 != -1 || *(_DWORD *)(v5 + 424) != 10047;
  if ( v2 != -1 )
    sub_141CC12C0(v2);
  return v6;
}
