/* x2 WSAConnect via cref @ 0x141ccf5d0 */
__int64 __fastcall sub_141CCF5D0(__int64 a1, __int64 *a2)
{
  __int64 v4; // rdi
  int namelen; // r8d
  __int64 v6; // rcx
  int *v7; // rdx
  __int64 v8; // rdi
  int v9; // r8d
  __int64 v10; // rdx
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v12; // rbx
  __int128 v14; // [rsp+40h] [rbp-38h] BYREF
  __int128 v15; // [rsp+50h] [rbp-28h] BYREF

  v14 = 0;
  v15 = 0;
  v4 = 0;
  namelen = 0;
  v6 = *a2;
  if ( *a2 )
  {
    v7 = *(int **)v6;
    if ( **(int **)v6 < 0 )
    {
      v8 = v6 + 16;
      v9 = *(_DWORD *)(v6 + 8);
    }
    else if ( v7 == (int *)&unk_1455B6860 )
    {
      v8 = *(_QWORD *)(v6 + 8);
      v9 = *(_DWORD *)(v6 + 16);
      if ( v9 < 0 )
        goto LABEL_18;
    }
    else if ( v7 == (int *)&unk_144D9FA90 )
    {
      v8 = *(_QWORD *)(v6 + 8);
      v9 = *(_DWORD *)(v6 + 16);
      if ( v9 < 0 )
        goto LABEL_18;
    }
    else
    {
      sub_141F83840(v6, &v15);
      v8 = v15;
      v9 = DWORD2(v15);
    }
    v10 = a2[1] & 0x7FFFFFFF;
    if ( v10 + (unsigned __int64)*((unsigned int *)a2 + 3) <= (unsigned int)v9 )
    {
      v4 = v10 + v8;
      namelen = *((_DWORD *)a2 + 3);
      goto LABEL_13;
    }
LABEL_18:
    sub_141D23C30();
    __debugbreak();
  }
LABEL_13:
  *(_QWORD *)&v14 = v4;
  DWORD2(v14) = namelen;
  if ( (unsigned int)sub_141CC25D0(a1, (const struct sockaddr **)&v14, namelen, nullptr, nullptr, nullptr, nullptr) != -1 )
    return 0;
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v12 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v12 )
    v12 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  return *(unsigned int *)(v12 + 424);
}
