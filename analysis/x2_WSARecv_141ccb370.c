/* x2 WSARecv via cref @ 0x141ccb370 */
__int64 __fastcall sub_141CCB370(__int64 a1, __int64 a2, __int64 a3)
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
  CHAR *buf; // rdx
  int v16; // eax
  __int64 v18; // [rsp+38h] [rbp-80h]
  __int128 v19; // [rsp+40h] [rbp-78h] BYREF
  __int128 v20; // [rsp+50h] [rbp-68h] BYREF
  __int128 lpNumberOfBytesRecvd_; // [rsp+60h] [rbp-58h] BYREF
  struct _WSABUF lpBuffers_; // [rsp+70h] [rbp-48h] BYREF
  __int128 lpOverlapped; // [rsp+80h] [rbp-38h] BYREF

  v19 = 0;
  v20 = 0;
  lpNumberOfBytesRecvd_ = 0;
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
    sub_141F83840(*(_QWORD *)(a1 + 256), &v20);
    v9 = v20;
    v10 = DWORD2(v20);
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
  DWORD2(lpNumberOfBytesRecvd_) = *(_DWORD *)(a1 + 236);
  v16 = sub_141CC2C70(
          a2,
          &lpBuffers_,
          1u,
          (DWORD *)&lpNumberOfBytesRecvd_,
          (DWORD *)&lpNumberOfBytesRecvd_ + 2,
          (struct _OVERLAPPED *)lpOverlapped,
          nullptr);
  v19 = *(_OWORD *)(a1 + 256);
  return sub_141CCAC00(a1, v16 == 0, lpNumberOfBytesRecvd_, (unsigned int)&lpOverlapped, (__int64)&v19, a3);
}
