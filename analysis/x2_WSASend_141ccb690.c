/* x2 WSASend via cref @ 0x141ccb690 */
__int64 __fastcall sub_141CCB690(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 v5; // rdi
  __int64 v6; // r14
  __int64 v7; // rax
  int *v8; // rdx
  __int64 v9; // r14
  int v10; // eax
  __int64 v11; // rdx
  __int64 v12; // rax
  __int64 v13; // rdx
  __int64 v14; // rdx
  CHAR *buf; // r9
  int v16; // eax
  __int64 v18; // [rsp+40h] [rbp-78h]
  _BYTE v19[24]; // [rsp+48h] [rbp-70h] BYREF
  __int128 v20; // [rsp+60h] [rbp-58h] BYREF
  struct _WSABUF lpBuffers_; // [rsp+70h] [rbp-48h] BYREF
  __int128 lpOverlapped; // [rsp+80h] [rbp-38h] BYREF

  memset(v19, 0, sizeof(v19));
  v20 = 0;
  lpBuffers_ = 0;
  lpOverlapped = 0;
  v5 = a1 + 256;
  v6 = 0;
  v7 = *(_QWORD *)(a1 + 256);
  if ( !v7 )
    goto LABEL_13;
  v8 = *(int **)v7;
  if ( **(int **)v7 < 0 )
  {
    v9 = v7 + 16;
    v10 = *(_DWORD *)(v7 + 8);
  }
  else if ( v8 == (int *)&unk_1455B6860 )
  {
    v9 = *(_QWORD *)(v7 + 8);
    v10 = *(_DWORD *)(v7 + 16);
    if ( v10 < 0 )
      goto LABEL_19;
  }
  else if ( v8 == (int *)&unk_144D9FA90 )
  {
    v9 = *(_QWORD *)(v7 + 8);
    v10 = *(_DWORD *)(v7 + 16);
    if ( v10 < 0 )
      goto LABEL_19;
  }
  else
  {
    sub_141F83840(*(_QWORD *)(a1 + 256), &v19[16]);
    v9 = *(_QWORD *)&v19[16];
    v10 = v20;
  }
  v11 = *(_DWORD *)(v5 + 8) & 0x7FFFFFFF;
  if ( v11 + (unsigned __int64)*(unsigned int *)(v5 + 12) > (unsigned int)v10 )
  {
LABEL_19:
    sub_141D23C30();
    __debugbreak();
  }
  v6 = v11 + v9;
LABEL_13:
  *((_QWORD *)&lpOverlapped + 1) = v6;
  v12 = *(_QWORD *)(a1 + 96);
  v13 = *(_QWORD *)(v12 + 8);
  if ( *(_BYTE *)(v13 + 32) )
    v14 = 0;
  else
    v14 = *(_QWORD *)(v13 + 24);
  v18 = v14;
  if ( !v14 )
    v18 = sub_141CC91B0(v12);
  *(_QWORD *)&lpOverlapped = sub_141D7CF20(v18, *(_QWORD *)(a1 + 168));
  buf = (CHAR *)(v6 + *(int *)(a1 + 208));
  lpBuffers_.len = *(_DWORD *)(a1 + 212);
  lpBuffers_.buf = buf;
  v16 = sub_141CC2E00(
          a2,
          &lpBuffers_,
          1u,
          (DWORD *)&v20 + 2,
          *(_DWORD *)(a1 + 236),
          (struct _OVERLAPPED *)lpOverlapped,
          nullptr);
  *(_OWORD *)v19 = *(_OWORD *)(a1 + 256);
  return sub_141CCAC00(a1, v16 == 0, DWORD2(v20), (unsigned int)&lpOverlapped, (__int64)v19, a3);
}
