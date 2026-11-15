/* entry 18 @ 0x143097940 */
__int64 __fastcall BrotliEncoderCompress(
        int a1,
        int n24,
        int a3,
        unsigned __int64 n0x1000000_3,
        __int64 a5,
        unsigned __int64 *a6,
        char *a7)
{
  unsigned __int64 n0x1000000_1; // rbp
  unsigned __int64 v11; // rcx
  __int64 n2; // rsi
  unsigned __int64 n0x1000000_4; // rax
  __int64 Instance; // rax
  __int64 Instance_1; // rbx
  unsigned __int64 n0x40000000_2; // r12
  int v18; // ecx
  __int64 v19; // r14
  size_t *v20; // r9
  unsigned __int64 v21; // r8
  unsigned __int64 v22; // rdx
  unsigned __int64 n0x40000000_4; // rcx
  unsigned __int64 n0x40000000_5; // rax
  unsigned __int64 n0x40000000_3; // rdi
  char v26; // al
  int v27; // ecx
  size_t v28; // r10
  size_t Size_2; // rax
  size_t Size; // rdi
  __int64 v31; // rcx
  __int64 v32; // rax
  int v33; // eax
  int v34; // edi
  int v35; // r14d
  unsigned __int64 n0x40000000_1; // rax
  unsigned int n0x40000000; // ecx
  bool v38; // zf
  int v39; // edi
  unsigned __int64 v40; // rax
  unsigned __int64 *v41; // r14
  unsigned __int64 n2_2; // rax
  __int64 v43; // rdi
  size_t n0x1000000; // r8
  int n2_4; // edx
  int v46; // ecx
  __int64 v47; // rsi
  __int64 n0x1000000_2; // rbx
  __int64 v49; // [rsp+40h] [rbp-78h]
  unsigned __int64 n2_1; // [rsp+48h] [rbp-70h]
  char *v51; // [rsp+50h] [rbp-68h]
  size_t Size_1; // [rsp+58h] [rbp-60h]
  unsigned __int64 v53; // [rsp+60h] [rbp-58h] BYREF
  char *v54; // [rsp+68h] [rbp-50h] BYREF
  unsigned __int64 v55; // [rsp+70h] [rbp-48h] BYREF
  __int64 v56; // [rsp+78h] [rbp-40h] BYREF
  unsigned __int64 n0x1000000_5; // [rsp+80h] [rbp-38h] BYREF
  unsigned __int64 n2_3; // [rsp+88h] [rbp-30h]
  __int64 v59; // [rsp+D8h] [rbp+20h]

  n0x1000000_1 = n0x1000000_3;
  v11 = *a6;
  n2 = 2;
  n2_3 = *a6;
  n0x1000000_4 = n0x1000000_3 + 4 * (n0x1000000_3 >> 14) + 6;
  if ( n0x1000000_3 )
  {
    if ( n0x1000000_4 < n0x1000000_3 )
      n0x1000000_4 = 0;
    n2_1 = n0x1000000_4;
  }
  else
  {
    n2_1 = 2;
  }
  if ( !v11 )
    return 0;
  if ( !n0x1000000_3 )
  {
    *a6 = 1;
    *a7 = 6;
    return 1;
  }
  Instance = BrotliEncoderCreateInstance(0, 0, 0);
  Instance_1 = Instance;
  if ( !Instance )
    return 0;
  n0x40000000_2 = n0x1000000_1;
  v18 = *(_DWORD *)(Instance + 6972);
  v49 = a5;
  v56 = a5;
  Size_1 = *a6;
  v55 = *a6;
  v51 = a7;
  v54 = a7;
  n0x1000000_5 = n0x1000000_1;
  v59 = 0;
  v53 = 0;
  if ( !v18 )
  {
    *(_QWORD *)(Instance + 24) = (unsigned int)n0x1000000_1;
    *(_DWORD *)(Instance + 4) = a1;
    *(_DWORD *)(Instance + 8) = n24;
    *(_DWORD *)Instance = a3;
  }
  if ( n24 > 24 && !v18 )
    *(_DWORD *)(Instance + 36) = 1;
  if ( !(unsigned int)sub_14309B6E0(Instance) || *(_DWORD *)(Instance_1 + 6960) != -1 || *(_DWORD *)(Instance_1 + 6964) )
  {
LABEL_70:
    v39 = 0;
    goto LABEL_71;
  }
  if ( *(_DWORD *)(Instance_1 + 4) <= 1u )
  {
    v39 = sub_143098210(
            Instance_1,
            2,
            (unsigned int)&n0x1000000_5,
            (unsigned int)&v56,
            (__int64)&v55,
            (__int64)&v54,
            (__int64)&v53);
    v40 = v53;
    goto LABEL_72;
  }
LABEL_19:
  v19 = v49;
LABEL_20:
  v20 = (size_t *)(Instance_1 + 6928);
  while ( 1 )
  {
    while ( 1 )
    {
      while ( 1 )
      {
        v21 = *(_QWORD *)(Instance_1 + 1424) - *(_QWORD *)(Instance_1 + 1520);
        v22 = 1LL << *(_DWORD *)(Instance_1 + 12);
        n0x40000000_4 = 0;
        if ( v21 < v22 )
          n0x40000000_4 = (1LL << *(_DWORD *)(Instance_1 + 12)) - v21;
        n0x40000000_5 = *(char *)(Instance_1 + 1611);
        if ( (n0x40000000_5 & 0x80u) == 0LL && n0x40000000_4 > n0x40000000_5 )
          n0x40000000_4 = *(char *)(Instance_1 + 1611);
        if ( !n0x40000000_4 || !n0x40000000_2 )
          break;
        n0x40000000_3 = n0x40000000_2;
        if ( n0x40000000_4 < n0x40000000_2 )
          n0x40000000_3 = n0x40000000_4;
        sub_143099380(Instance_1, n0x40000000_3, v19, v20);
        v26 = *(_BYTE *)(Instance_1 + 1611);
        v20 = (size_t *)(Instance_1 + 6928);
        *(_QWORD *)(Instance_1 + 6912) += n0x40000000_3;
        v19 += n0x40000000_3;
        n0x40000000_2 -= n0x40000000_3;
        v49 = v19;
        if ( v26 > 0 )
        {
          *(_BYTE *)(Instance_1 + 1611) = v26 - n0x40000000_3;
          goto LABEL_20;
        }
      }
      v27 = *(_DWORD *)(Instance_1 + 6964);
      if ( v27 != 1 || !*(_BYTE *)(Instance_1 + 1610) )
        break;
      sub_14309BFE0(Instance_1, v22, v21, v20);
      v28 = *(_QWORD *)(Instance_1 + 6928);
LABEL_42:
      v20 = (size_t *)(Instance_1 + 6928);
      if ( *(_BYTE *)(Instance_1 + 1611) == 0xFF )
      {
        v33 = *(_DWORD *)(Instance_1 + 6964);
        v20 = (size_t *)(Instance_1 + 6928);
        if ( v33 == 1 )
        {
          if ( !v28 )
          {
            *(_DWORD *)(Instance_1 + 6964) = 0;
            *(_QWORD *)(Instance_1 + 6920) = 0;
            *(_BYTE *)(Instance_1 + 1611) = -2;
            goto LABEL_20;
          }
        }
        else if ( !v33 )
        {
          *(_BYTE *)(Instance_1 + 1611) = -2;
          goto LABEL_20;
        }
      }
    }
    Size_2 = *v20;
    if ( *v20 )
    {
      if ( Size_1 )
      {
        Size = Size_1;
        if ( Size_2 < Size_1 )
          Size = *v20;
        memcpy(v51, *(const void **)(Instance_1 + 6920), Size);
        v28 = *(_QWORD *)(Instance_1 + 6928) - Size;
        v51 += Size;
        v31 = Size + *(_QWORD *)(Instance_1 + 6936);
        *(_QWORD *)(Instance_1 + 6920) += Size;
        v32 = -1;
        Size_1 -= Size;
        *(_QWORD *)(Instance_1 + 6928) = v28;
        if ( v31 != -1 )
          v32 = v31;
        *(_QWORD *)(Instance_1 + 6936) = v31;
        v59 = v32;
        goto LABEL_42;
      }
      if ( Size_2 )
        break;
    }
    if ( v27 )
      break;
    v34 = 0;
    if ( n0x40000000_2 )
    {
      v35 = 0;
      if ( !*(_BYTE *)(Instance_1 + 1611) )
      {
        *(_BYTE *)(Instance_1 + 1611) = -1;
        v34 = 1;
      }
    }
    else
    {
      v35 = 1;
    }
    if ( !*(_QWORD *)(Instance_1 + 24) )
    {
      n0x40000000_1 = *(_QWORD *)(Instance_1 + 1424) - *(_QWORD *)(Instance_1 + 1520);
      if ( n0x40000000_1 >= 0x40000000
        || n0x40000000_2 >= 0x40000000
        || (n0x40000000 = n0x40000000_1 + n0x40000000_2, n0x40000000_1 + n0x40000000_2 >= 0x40000000) )
      {
        n0x40000000 = 0x40000000;
      }
      *(_QWORD *)(Instance_1 + 24) = n0x40000000;
    }
    if ( !(unsigned int)sub_143099730(Instance_1, v35, v34, (_DWORD)v20, Instance_1 + 6920) )
      goto LABEL_70;
    if ( v34 )
      *(_DWORD *)(Instance_1 + 6964) = 1;
    v38 = v35 == 0;
    v20 = (size_t *)(Instance_1 + 6928);
    v19 = v49;
    if ( !v38 )
    {
      *(_DWORD *)(Instance_1 + 6964) = 2;
      goto LABEL_19;
    }
  }
  if ( v27 == 1 && !Size_2 )
  {
    *(_DWORD *)(Instance_1 + 6964) = 0;
    *(_QWORD *)(Instance_1 + 6920) = 0;
  }
  v39 = 1;
LABEL_71:
  v40 = v59;
LABEL_72:
  if ( *(_DWORD *)(Instance_1 + 6964) != 2 || *(_QWORD *)(Instance_1 + 6928) )
  {
    v41 = a6;
    *a6 = v40;
    BrotliEncoderDestroyInstance(Instance_1);
    n2_2 = n2_1;
  }
  else
  {
    v41 = a6;
    *a6 = v40;
    BrotliEncoderDestroyInstance(Instance_1);
    n2_2 = n2_1;
    if ( v39 && (!n2_1 || *a6 <= n2_1) )
      return 1;
  }
  *v41 = 0;
  if ( !n2_2 || n2_3 < n2_2 )
    return 0;
  v43 = 0;
  *(_WORD *)a7 = 801;
  do
  {
    n0x1000000 = (unsigned int)n0x1000000_1;
    n2_4 = 0;
    if ( n0x1000000_1 > 0x1000000 )
      n0x1000000 = 0x1000000;
    if ( (unsigned int)n0x1000000 > 0x10000 )
    {
      LOBYTE(n2_4) = (unsigned int)n0x1000000 > 0x100000;
      ++n2_4;
    }
    v46 = (2 * (n2_4 | (4 * n0x1000000 - 4))) | (1 << (4 * n2_4 + 19));
    *(_WORD *)&a7[n2] = v46;
    a7[n2 + 2] = BYTE2(v46);
    v47 = n2 + 3;
    if ( n2_4 == 2 )
      a7[v47++] = HIBYTE(v46);
    n0x1000000_2 = (unsigned int)n0x1000000;
    memcpy(&a7[v47], (const void *)(v43 + a5), n0x1000000);
    n2 = n0x1000000_2 + v47;
    v43 += n0x1000000_2;
    n0x1000000_1 -= n0x1000000_2;
  }
  while ( n0x1000000_1 );
  a7[n2] = 3;
  *a6 = n2 + 1;
  return 1;
}
