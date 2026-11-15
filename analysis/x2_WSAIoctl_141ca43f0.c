/* x2 WSAIoctl via cref @ 0x141ca43f0 */
__int64 __fastcall sub_141CA43F0(__int64 a1, char a2, char a3)
{
  __int64 v6; // r14
  _QWORD *v7; // r15
  __int64 v8; // r12
  __int64 v9; // r12
  __int64 v10; // r13
  __int64 v11; // r13
  __int64 v12; // r13
  __int64 v13; // rax
  __int64 v14; // rcx
  __int64 v15; // rbx
  __int64 v16; // rdi
  __int64 v17; // rax
  __int64 v18; // rbx
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v20; // rdi
  unsigned int n10035; // edi
  _UNKNOWN **v22; // rdx
  __int64 v23; // rbx
  __int64 v24; // rax
  __int64 v25; // rbx
  __int64 v26; // rsi
  __int64 v27; // rax
  __int64 v28; // rbx
  _QWORD *ThreadLocalStoragePointer_1; // rcx
  __int64 v30; // rsi
  unsigned int n10035_1; // esi
  _UNKNOWN **v32; // rdx
  __int64 v33; // rbx
  __int64 v34; // rax
  __int64 v35; // rbx
  __int64 v36; // rbx
  __int64 v38; // [rsp+48h] [rbp-60h]
  DWORD lpcbBytesReturned_; // [rsp+50h] [rbp-58h] BYREF
  DWORD lpcbBytesReturned[18]; // [rsp+58h] [rbp-50h] BYREF

  if ( *((_QWORD *)&byte_14727A880 - 1) )
    sub_142F806A0();
  v6 = qword_1472AD078;
  v38 = *(_QWORD *)(qword_1472AD078 + 64);
  sub_141D6D5C0(v38);
  lpcbBytesReturned[3] = 1;
  v7 = (_QWORD *)qword_1472AD080;
  if ( !*(_QWORD *)(qword_1472AD080 + 8) )
  {
    if ( *((_QWORD *)&unk_14727A928 - 1) )
      ((void (*)(void))sub_142F744F8)();
    if ( unk_14727A929 )
    {
      v8 = sub_143019350(&unk_144DA0808);
      sub_141CC5760(v8, 2, 2, 0);
      sub_141CC5E80(v8, 0);
      sub_143019570(v7 + 1, v8);
      v9 = sub_143019310(&unk_144DAC0C8);
      sub_141D718C0(v9, 0, 0);
      sub_143019570(v7 + 3, v9);
    }
    if ( unk_14727A928 )
    {
      v10 = sub_143019350(&unk_144DA0808);
      sub_141CC5760(v10, 23, 2, 0);
      sub_141CC5E80(v10, 0);
      sub_143019570(v7 + 2, v10);
      v11 = sub_143019310(&unk_144DAC0C8);
      sub_141D718C0(v11, 0, 0);
      sub_143019570(v7 + 4, v11);
    }
  }
  if ( a1 )
  {
    v12 = *(_QWORD *)(v6 + 8);
    if ( a2 )
      v13 = sub_141D71A30();
    else
      v13 = 0;
    sub_1429D0740(v12, a1, v13, 0);
  }
  if ( !byte_1473E9DAC )
  {
    v14 = (unsigned int)(*(_DWORD *)(*(_QWORD *)(v6 + 8) + 56LL) - *(_DWORD *)(*(_QWORD *)(v6 + 8) + 64LL));
    if ( (_DWORD)v14 )
    {
      if ( !algn_1473E9DAD[0] )
      {
        if ( *((_QWORD *)&unk_14727A928 - 1) )
          sub_142F744F8(v14);
        if ( unk_14727A929 && (a3 & 1) != 0 )
        {
          v15 = sub_143019310(&unk_144DACD20);
          v16 = v7[3];
          sub_142FD8E5A(v15, 0);
          v17 = sub_143019310(&unk_144D9E028);
          *(_DWORD *)(v17 + 8) = 1;
          sub_141D7D930(v16, v15, v17, -1, 1, 1);
          if ( (unsigned int)sub_141CA35A0(
                               *(_QWORD *)(v7[1] + 8LL),
                               0x28000017u,
                               0,
                               0,
                               0,
                               0,
                               lpcbBytesReturned,
                               nullptr,
                               nullptr) )
          {
            v18 = sub_143019310(&unk_144D9DD18);
            ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
            v20 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
            if ( !v20 )
              v20 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
            n10035 = *(_DWORD *)(v20 + 424);
            v22 = (_UNKNOWN **)sub_141DF4AE0(n10035, 0);
            if ( !v22 )
              v22 = &off_146CFF1C8;
            *(_DWORD *)(v18 + 72) = -2146233088;
            sub_143019570(v18 + 8, v22);
            *(_DWORD *)(v18 + 72) = -2147467259;
            *(_DWORD *)(v18 + 80) = n10035;
            if ( n10035 != 10035 )
            {
              sub_1430198D0(v18);
              __debugbreak();
            }
          }
          v23 = *(_QWORD *)(v7[1] + 8LL);
          v24 = sub_141D7C040(v7[3]);
          if ( (unsigned int)sub_141CA3420(v23, v24, 512) )
          {
            v35 = sub_143019310(&unk_144D9DD18);
            sub_141CA4CF0(v35);
            sub_1430198D0(v35);
            __debugbreak();
          }
        }
        if ( unk_14727A928 && (a3 & 2) != 0 )
        {
          v25 = sub_143019310(&unk_144DACD20);
          v26 = v7[4];
          sub_142FD8E5A(v25, 0);
          v27 = sub_143019310(&unk_144D9E028);
          *(_DWORD *)(v27 + 8) = 2;
          sub_141D7D930(v26, v25, v27, -1, 1, 1);
          if ( (unsigned int)sub_141CA35A0(
                               *(_QWORD *)(v7[2] + 8LL),
                               0x28000017u,
                               0,
                               0,
                               0,
                               0,
                               &lpcbBytesReturned_,
                               nullptr,
                               nullptr) )
          {
            v28 = sub_143019310(&unk_144D9DD18);
            ThreadLocalStoragePointer_1 = NtCurrentTeb()->ThreadLocalStoragePointer;
            v30 = *(_QWORD *)(ThreadLocalStoragePointer_1[TlsIndex] + 16LL);
            if ( !v30 )
              v30 = sub_141DED040(ThreadLocalStoragePointer_1[TlsIndex] + 16LL);
            n10035_1 = *(_DWORD *)(v30 + 424);
            v32 = (_UNKNOWN **)sub_141DF4AE0(n10035_1, 0);
            if ( !v32 )
              v32 = &off_146CFF1C8;
            *(_DWORD *)(v28 + 72) = -2146233088;
            sub_143019570(v28 + 8, v32);
            *(_DWORD *)(v28 + 72) = -2147467259;
            *(_DWORD *)(v28 + 80) = n10035_1;
            if ( n10035_1 != 10035 )
            {
              sub_1430198D0(v28);
              __debugbreak();
            }
          }
          v33 = *(_QWORD *)(v7[2] + 8LL);
          v34 = sub_141D7C040(v7[4]);
          if ( (unsigned int)sub_141CA3420(v33, v34, 512) )
          {
            v36 = sub_143019310(&unk_144D9DD18);
            sub_141CA4CF0(v36);
            sub_1430198D0(v36);
            __debugbreak();
          }
        }
      }
      *(_WORD *)&byte_1473E9DAC = 257;
    }
  }
  return sub_141D6D8C0(v38);
}
