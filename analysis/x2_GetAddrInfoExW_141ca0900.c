/* x2 GetAddrInfoExW via cref @ 0x141ca0900 */
__int64 __fastcall sub_141CA0900(__int64 a1, char a2, char a3, unsigned __int8 a4, int n2_1, __int64 a6)
{
  __int64 v6; // rbx
  __int64 v9; // rsi
  int v10; // r14d
  int v11; // edx
  __int64 v12; // r15
  __int64 result; // rax
  int n2_2; // ebp
  LARGE_INTEGER v15; // r15
  __int64 v16; // rdi
  int n2_3; // edi
  LARGE_INTEGER v18; // rbx
  __int64 v19; // rsi
  int n2_4; // edi
  __int64 v21; // rbp
  __int64 v22; // rbx
  int n2_5; // ebx
  __int64 v24; // rdi
  __int64 v25; // rdx
  __int64 v26; // r14
  __int64 v27; // rdx
  __int64 v28; // r15
  int n2; // ecx
  _UNKNOWN **v30; // r14
  __int64 v31; // r15
  __int64 v32; // rsi
  __int64 v33; // rbx
  __int64 v34; // r14
  __int64 v35; // rbx
  void **v36; // rbx
  __int64 v37; // rsi
  __int64 v38; // rbx
  __int128 v39; // [rsp+20h] [rbp-58h] BYREF
  LARGE_INTEGER PerformanceCount[2]; // [rsp+30h] [rbp-48h] BYREF
  void **v41; // [rsp+40h] [rbp-38h] BYREF
  __int64 v42; // [rsp+80h] [rbp+8h]

  v39 = 0;
  *(_OWORD *)&PerformanceCount[0].LowPart = 0;
  v41 = nullptr;
  v6 = a1;
  v9 = a6;
  if ( !a1 )
  {
    sub_141CFC3F0(&off_14702C590);
    __debugbreak();
  }
  if ( a6 && *(_DWORD *)(a6 + 32) )
  {
    if ( a4 )
      return sub_142E1DA70(&off_144A5D3F8, a6);
    else
      return sub_142E1DA70(&off_144966E38, a6);
  }
  v10 = a4;
  if ( (unsigned int)sub_141CA0450(&n2_1, a1, a4, &v41, v39, *((_QWORD *)&v39 + 1)) )
  {
    v11 = *(_DWORD *)(v6 + 8);
    *(_QWORD *)&v39 = v6 + 12;
    DWORD2(v39) = v11;
    v12 = sub_142D03AE0(&v39, 1);
    if ( v12 )
    {
      if ( a3 )
      {
        if ( off_14727A8B0[-1] )
          sub_142F806F8();
        v22 = qword_1472AD0A8;
        if ( (unsigned int)sub_141CAB3F0(v12, *(_QWORD *)(qword_1472AD0A8 + 8))
          || (unsigned int)sub_141CAB3F0(v12, *(_QWORD *)(v22 + 40)) )
        {
          v38 = sub_143019310(&unk_144DA4408);
          sub_141CFC1B0(v38, &off_146D9A3F8, &off_14702C590);
          sub_1430198D0(v38);
          __debugbreak();
        }
      }
      if ( !a2 )
      {
        if ( n2_1 )
        {
          n2_5 = n2_1;
          v24 = sub_143019310(&unk_1454D1688);
          sub_143019570(v24 + 8, v12);
          *(_DWORD *)(v24 + 16) = n2_5;
          v6 = v24;
        }
        else
        {
          v6 = v12;
        }
LABEL_32:
        if ( v10 )
        {
          v27 = *(_QWORD *)(qword_1472AD058 + 32);
          if ( !v27 )
          {
            v28 = sub_143019310(&unk_14550C068);
            sub_142FBBF02(v28, &off_14725DDE0);
            sub_143019570(qword_1472AD058 + 32, v28);
            v27 = v28;
          }
          return sub_142E6B590(&off_144A5D2B0, v27, v6, v9);
        }
        else
        {
          v25 = *(_QWORD *)(qword_1472AD058 + 40);
          if ( !v25 )
          {
            v26 = sub_143019310(&unk_14550BFF0);
            sub_142FBBF0E(v26, &off_14725DDE0);
            sub_143019570(qword_1472AD058 + 40, v26);
            v25 = v26;
          }
          return sub_142E6B590(&off_144966DA0, v25, v6, v9);
        }
      }
      if ( v10 )
      {
        if ( !n2_1 )
          goto LABEL_44;
        n2 = 2;
        if ( *(_QWORD *)(v12 + 8) )
          n2 = 23;
        if ( n2 != n2_1 )
        {
          v30 = &off_14721A868;
        }
        else
        {
LABEL_44:
          v30 = (_UNKNOWN **)sub_1430194A0(&unk_145DC4138, 1);
          sub_143019570(v30 + 2, v12);
        }
        v31 = sub_143019310(&unk_145D44CC0);
        *(_DWORD *)(v31 + 52) = 0x1000000;
        sub_143019570(v31 + 56, v30);
        return v31;
      }
      else
      {
        v32 = sub_141CA0ED0(v12);
        if ( v32 )
        {
          v33 = sub_143019310(&unk_1454C8220);
          *(_DWORD *)(v33 + 52) = 0x1000000;
          sub_143019570(v33 + 56, v32);
        }
        else
        {
          if ( *(&qword_14728BA58 - 1) )
            sub_142F826DA();
          return *(_QWORD *)(qword_1472BF190 + 8);
        }
        return v33;
      }
    }
    else
    {
      if ( !(unsigned int)sub_141CA1EF0() )
        goto LABEL_21;
      sub_141CA0F50(v6);
      if ( (unsigned int)sub_141CA1650() )
      {
        if ( v10 )
        {
          v42 = v6;
          a6 = v9;
          n2_2 = n2_1;
          QueryPerformanceCounter(PerformanceCount);
          v15 = PerformanceCount[0];
          v16 = sub_141CA22B0(v6, v10, n2_2, a6);
          if ( dword_14751A980 )
            sub_14301A090();
          result = v16
                 ? ((__int64 (__fastcall *)(_QWORD, _QWORD, _QWORD, _QWORD))sub_142E6B840)(
                     &off_144A5D2D8,
                     v16,
                     v6,
                     (LARGE_INTEGER)v15.QuadPart)
                 : 0LL;
        }
        else
        {
          v42 = v6;
          a6 = v9;
          n2_3 = n2_1;
          QueryPerformanceCounter(&PerformanceCount[1]);
          v18 = PerformanceCount[1];
          v19 = sub_141CA22B0(v42, 0, n2_3, a6);
          if ( dword_14751A980 )
            sub_14301A090();
          result = v19
                 ? ((__int64 (__fastcall *)(_QWORD, _QWORD, _QWORD, _QWORD))sub_142E6B840)(
                     &off_144966DC8,
                     v19,
                     v42,
                     (LARGE_INTEGER)v18.QuadPart)
                 : 0LL;
        }
      }
      else
      {
        v42 = v6;
        a6 = v9;
        result = sub_141CA22B0(v6, v10, n2_1, v9);
      }
      v6 = v42;
      v9 = a6;
      if ( !result )
      {
LABEL_21:
        if ( n2_1 )
        {
          n2_4 = n2_1;
          v21 = sub_143019310(&unk_145560508);
          sub_143019570(v21 + 8, v6);
          *(_DWORD *)(v21 + 16) = n2_4;
          v6 = v21;
        }
        goto LABEL_32;
      }
    }
  }
  else if ( v10 )
  {
    v34 = (__int64)v41;
    if ( v41 && *v41 != &unk_145DC4138 )
      v34 = sub_141DB9D40();
    if ( v34 )
    {
      v35 = sub_143019310(&unk_145D44CC0);
      *(_DWORD *)(v35 + 52) = 0x1000000;
      sub_143019570(v35 + 56, v34);
    }
    else
    {
      if ( *(&qword_1472A5B10 - 1) )
        sub_142F83770();
      return *(_QWORD *)(qword_1472D9F88 + 8);
    }
    return v35;
  }
  else
  {
    v36 = v41;
    if ( v41 && *v41 != &unk_144D9D3B0 )
    {
      sub_141DB9ED0();
      __debugbreak();
    }
    if ( v41 )
    {
      v37 = sub_143019310(&unk_1454C8220);
      *(_DWORD *)(v37 + 52) = 0x1000000;
      sub_143019570(v37 + 56, v36);
    }
    else
    {
      if ( *(&qword_14728BA58 - 1) )
        sub_142F826DA();
      return *(_QWORD *)(qword_1472BF190 + 8);
    }
    return v37;
  }
  return result;
}
