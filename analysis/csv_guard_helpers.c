==== string_normalise ====
__int64 __fastcall sub_141CFA390(__int64 a1)
{
  int v2; // esi
  int v3; // eax
  int v4; // eax

  v2 = *(_DWORD *)(a1 + 8);
  if ( v2
    && (*(unsigned __int16 *)(a1 + 12) < 0x100u ? (v3 = sub_141D073A0()) : (v3 = sub_141D45100()),
        v3
     || (*(unsigned __int16 *)(a1 + 2LL * (unsigned int)(v2 - 1) + 12) < 0x100u
       ? (v4 = sub_141D073A0())
       : (v4 = sub_141D45100()),
         v4)) )
  {
    return sub_141CFA500(a1, 3);
  }
  else
  {
    return a1;
  }
}


==== list_lookup ====
__int64 __fastcall sub_142E74840(__int64 a1, __int64 a2, __int64 a3, _BYTE *a4)
{
  __int64 v7; // r14
  __int64 v8; // r14
  __int64 v9; // r15
  int v11; // esi
  __int64 v12; // r15
  __int64 v13; // r15
  __int64 v14; // r14
  __int64 v15; // r13

  if ( !a2 )
  {
    sub_141BF8DF0(17);
    __debugbreak();
  }
  if ( !a3 )
  {
    sub_141BF8DF0(12);
    __debugbreak();
  }
  v7 = *(_QWORD *)(a1 + 24);
  if ( *(_QWORD *)a2 == *(_QWORD *)(v7 + 24) )
  {
    v13 = a2 + 16;
    v11 = *(_DWORD *)(a2 + 8);
  }
  else
  {
    if ( *(_QWORD *)a2 != *(_QWORD *)(v7 + 16) )
    {
      v8 = (**(__int64 (__fastcall ***)(__int64))(a1 + 8))(a2);
      while ( (unsigned int)off_147322250(v8) )
      {
        v9 = (**(__int64 (__fastcall ***)(__int64))(a1 + 16))(v8);
        if ( (*(unsigned int (__fastcall **)(_QWORD, __int64))(a3 + 32))(*(_QWORD *)(a3 + 8), v9) )
        {
          *a4 = 1;
          sub_142E74998();
          return v9;
        }
      }
      off_147312630(v8);
      goto LABEL_17;
    }
    v11 = *(_DWORD *)(a2 + 16);
    v12 = *(_QWORD *)(a2 + 8);
    if ( *(_DWORD *)(v12 + 8) < (unsigned int)v11 )
    {
      sub_141D2E1D0();
      __debugbreak();
    }
    v13 = v12 + 16;
  }
  if ( v11 <= 0 )
  {
LABEL_17:
    *a4 = 0;
    return 0;
  }
  v14 = 0;
  while ( 1 )
  {
    v15 = *(_QWORD *)(v13 + v14);
    if ( (*(unsigned int (__fastcall **)(_QWORD, __int64))(a3 + 32))(*(_QWORD *)(a3 + 8), v15) )
      break;
    v14 += 8;
    if ( !--v11 )
      goto LABEL_17;
  }
  *a4 = 1;
  return v15;
}


==== country_error_sink ====
__int64 __fastcall sub_141CF6EA0(__int64 a1, __int64 a2, __int64 a3)
{
  unsigned int n0x100; // edx
  __int64 result; // rax
  char v8; // [rsp+0h] [rbp-200h] BYREF
  __int64 __security_cookie; // [rsp+200h] [rbp+0h]
  __int64 v10; // [rsp+208h] [rbp+8h] BYREF
  __int128 v11; // [rsp+210h] [rbp+10h]
  __int64 v12; // [rsp+220h] [rbp+20h]

  v10 = 0;
  v11 = 0;
  v12 = 0;
  if ( !a2 )
  {
    sub_141D05BF0(&off_147038B88);
    __debugbreak();
  }
  v10 = 0;
  *((_QWORD *)&v11 + 1) = &v8;
  LODWORD(v12) = 256;
  LODWORD(v11) = 0;
  n0x100 = *(_DWORD *)(a2 + 8) + 8 * *(_DWORD *)(a3 + 8);
  if ( n0x100 > 0x100 )
    sub_141DA2AB0(&v10, n0x100 - (unsigned int)v11);
  sub_141DA1FC0(&v10, a1, a2, a3);
  result = sub_141DA2820(&v10);
  if ( __security_cookie != _security_cookie )
    return sub_143028970();
  return result;
}


==== state_error_sink ====
__int64 __fastcall sub_141CF6BF0(__int64 a1)
{
  __int128 v3; // [rsp+20h] [rbp-28h] BYREF
  __int128 v4; // [rsp+30h] [rbp-18h] BYREF

  v3 = 0;
  v4 = 0;
  sub_141D1FDF0(&v4);
  sub_142D3D750(&v3, &off_1449848A0, &v4, 2);
  return sub_141CF6EA0(0, a1, (__int64)&v3);
}


