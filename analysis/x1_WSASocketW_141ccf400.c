/* x1 WSASocketW via cref @ 0x141ccf400 */
__int64 __fastcall sub_141CCF400(int a1, int type, int protocol, _QWORD *a4)
{
  __int64 v8; // rax
  SOCKET v9; // rbx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v12; // rdi
  unsigned int v14; // esi
  __int64 v15; // rbx
  __int64 v16; // [rsp+48h] [rbp-70h]
  _BYTE v17[96]; // [rsp+50h] [rbp-68h] BYREF
  _QWORD *v18; // [rsp+D8h] [rbp+20h]

  if ( !dword_1473E9DB0 )
    sub_141CC2F70();
  v8 = sub_143019350(&unk_144DA0790);
  *(_QWORD *)(v8 + 8) = -1;
  *(_DWORD *)(v8 + 16) = 4;
  *(_BYTE *)(v8 + 20) = 1;
  *(_BYTE *)(v8 + 21) = 1;
  *(_BYTE *)(v8 + 23) = 1;
  sub_1430195E0(a4, v8);
  v18 = a4;
  v16 = *a4;
  SetLastError(0);
  sub_14301AE60(v17);
  v9 = WSASocketW(a1, type, protocol, nullptr, 0, WSA_FLAG_OVERLAPPED | 128);
  sub_14301AEB0(v17);
  LastError = GetLastError();
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v12 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v12 )
    v12 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v12 + 424) = LastError;
  *(_QWORD *)(v16 + 8) = v9;
  if ( !(*(unsigned int (__fastcall **)(_QWORD))(*(_QWORD *)*v18 + 48LL))(*v18) )
    return 0;
  v14 = *(_DWORD *)(v12 + 424);
  v15 = *v18;
  (*(void (__fastcall **)(__int64, __int64))(*(_QWORD *)v15 + 56LL))(v15, 1);
  sub_141CE7170(v15);
  return v14;
}
