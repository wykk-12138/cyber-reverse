/* entry 19 @ 0x143097ef0 */
__int64 __fastcall BrotliEncoderCompressStream(
        __int64 Instance,
        int n3,
        unsigned __int64 *p_n0x1000000,
        _QWORD *a4,
        __int64 a5,
        __int64 a6,
        __int64 a7)
{
  __int64 v11; // r9
  __int64 v12; // rax
  __int64 n0x40000000; // rax
  unsigned __int64 n0x40000000_1; // rcx
  int n3_1; // eax
  int v17; // ecx
  unsigned __int64 n0x1000000_1; // rdi
  unsigned __int64 v19; // r8
  unsigned __int64 n0x1000000_2; // rax
  unsigned __int64 n0x1000000; // rsi
  char v22; // al
  int v23; // eax
  __int64 v24; // rax
  int v25; // edi
  int v26; // esi

  if ( !(unsigned int)sub_14309B6E0(Instance) )
    return 0;
  v12 = *(unsigned int *)(Instance + 6960);
  if ( (_DWORD)v12 != -1 )
  {
    if ( *p_n0x1000000 != v12 || n3 != 3 )
      return 0;
LABEL_7:
    if ( !*(_QWORD *)(Instance + 24) )
    {
      n0x40000000 = 0x40000000;
      n0x40000000_1 = *(_QWORD *)(Instance + 1424) - *(_QWORD *)(Instance + 1520);
      if ( n0x40000000_1 < 0x40000000 )
        n0x40000000 = (unsigned int)n0x40000000_1;
      *(_QWORD *)(Instance + 24) = n0x40000000;
    }
    return sub_14309CAE0(Instance, (_DWORD)p_n0x1000000, (_DWORD)a4, a5, a6, a7);
  }
  if ( n3 == 3 )
    goto LABEL_7;
  n3_1 = *(_DWORD *)(Instance + 6964);
  if ( n3_1 == 3 || n3_1 == 4 || n3_1 && *p_n0x1000000 )
    return 0;
  if ( *(_DWORD *)(Instance + 4) <= 1u )
    return sub_143098210(Instance, n3, (unsigned int)p_n0x1000000, (unsigned int)a4, a5, a6, a7);
  while ( 1 )
  {
    while ( 1 )
    {
      while ( 1 )
      {
        v17 = *(_DWORD *)(Instance + 12);
        n0x1000000_1 = 0;
        v19 = *(_QWORD *)(Instance + 1424) - *(_QWORD *)(Instance + 1520);
        if ( v19 < 1LL << v17 )
          n0x1000000_1 = (1LL << v17) - v19;
        n0x1000000_2 = *(char *)(Instance + 1611);
        if ( (n0x1000000_2 & 0x80u) == 0LL && n0x1000000_1 > n0x1000000_2 )
          n0x1000000_1 = *(char *)(Instance + 1611);
        if ( !n0x1000000_1 )
          break;
        n0x1000000 = *p_n0x1000000;
        if ( !*p_n0x1000000 )
          break;
        if ( n0x1000000_1 < n0x1000000 )
          n0x1000000 = n0x1000000_1;
        sub_143099380(Instance, n0x1000000, *a4, v11);
        *a4 += n0x1000000;
        *p_n0x1000000 -= n0x1000000;
        *(_QWORD *)(Instance + 6912) += n0x1000000;
        v22 = *(_BYTE *)(Instance + 1611);
        if ( v22 > 0 )
          *(_BYTE *)(Instance + 1611) = v22 - n0x1000000;
      }
      if ( !(unsigned int)sub_14309C060(Instance, a5, a6, a7) )
        break;
      if ( *(_BYTE *)(Instance + 1611) == 0xFF )
      {
        v23 = *(_DWORD *)(Instance + 6964);
        if ( v23 == 1 )
        {
          if ( !*(_QWORD *)(Instance + 6928) )
          {
            *(_DWORD *)(Instance + 6964) = 0;
            *(_QWORD *)(Instance + 6920) = 0;
            *(_BYTE *)(Instance + 1611) = -2;
          }
        }
        else if ( !v23 )
        {
          *(_BYTE *)(Instance + 1611) = -2;
        }
      }
    }
    v24 = *(_QWORD *)(Instance + 6928);
    if ( v24 || *(_DWORD *)(Instance + 6964) || n0x1000000_1 && !n3 )
      break;
    if ( !*p_n0x1000000 && n3 == 2 )
    {
      v25 = 1;
LABEL_42:
      v26 = 0;
      if ( v25 )
        goto LABEL_45;
      goto LABEL_43;
    }
    v25 = 0;
    if ( *p_n0x1000000 || n3 != 1 )
      goto LABEL_42;
    v26 = 1;
LABEL_43:
    if ( !*(_BYTE *)(Instance + 1611) )
    {
      *(_BYTE *)(Instance + 1611) = -1;
      v26 = 1;
    }
LABEL_45:
    sub_14309D700(Instance, *p_n0x1000000);
    if ( !(unsigned int)sub_143099730(Instance, v25, v26, (int)Instance + 6928, Instance + 6920) )
      return 0;
    if ( v26 )
      *(_DWORD *)(Instance + 6964) = 1;
    if ( v25 )
      *(_DWORD *)(Instance + 6964) = 2;
  }
  if ( *(_DWORD *)(Instance + 6964) == 1 && !v24 )
  {
    *(_DWORD *)(Instance + 6964) = 0;
    *(_QWORD *)(Instance + 6920) = 0;
  }
  return 1;
}
