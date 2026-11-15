/* entry 17 @ 0x143097740 */
_BOOL8 __fastcall BrotliEncoderAttachPreparedDictionary(__int64 a1, int *a2)
{
  int v2; // eax
  int *v3; // rsi
  __int64 v5; // rdi
  __int64 v6; // rax
  __int128 *v7; // rbx
  __int64 v8; // rax
  int v9; // ecx
  unsigned __int64 v10; // rbp
  _QWORD *v11; // r14
  __int64 n6; // rax
  __int128 v13; // xmm0
  int v15; // [rsp+60h] [rbp+8h]
  int v16; // [rsp+68h] [rbp+10h]

  v2 = *a2;
  v3 = a2;
  if ( *a2 == -558043678 )
  {
    v3 = *((int **)a2 + 4);
    v2 = *v3;
  }
  if ( v2 != -558043680 && v2 != -558043677 )
  {
    if ( v2 == -558043679 )
    {
      v5 = a1 + 624;
      if ( *(_DWORD *)(a1 + 624)
        || *(_BYTE *)(a1 + 628) != 1
        || (v6 = *(_QWORD *)(a1 + 696), *(_UNKNOWN **)(v6 + 24) != &unk_14629DD80)
        || (v16 = 1, *(_UNKNOWN **)(v6 + 32) != &unk_1462ADD80) )
      {
        v16 = 0;
      }
      v7 = (__int128 *)(v3 + 136);
      if ( v3[136]
        || *((_BYTE *)v3 + 548) != 1
        || (v8 = *((_QWORD *)v3 + 77), *(_UNKNOWN **)(v8 + 24) != &unk_14629DD80)
        || (v15 = 1, *(_UNKNOWN **)(v8 + 32) != &unk_1462ADD80) )
      {
        v15 = 0;
      }
      if ( !*(_DWORD *)(a1 + 6972) )
      {
        v9 = v3[328];
        v10 = 0;
        if ( *(_DWORD *)(a1 + 1392) < v9 )
          v9 = *(_DWORD *)(a1 + 1392);
        *(_DWORD *)(a1 + 1392) = v9;
        if ( *((_QWORD *)v3 + 1) )
        {
          v11 = v3 + 6;
          while ( (unsigned int)sub_14309DE50(a1 + 88, *v11) )
          {
            ++v10;
            ++v11;
            if ( v10 >= *((_QWORD *)v3 + 1) )
              goto LABEL_23;
          }
          return 0;
        }
LABEL_23:
        if ( v15 )
          return 1;
        if ( v16 )
        {
          n6 = 6;
          do
          {
            v5 += 128;
            v13 = *v7;
            v7 += 8;
            *(_OWORD *)(v5 - 128) = v13;
            *(_OWORD *)(v5 - 112) = *(v7 - 7);
            *(_OWORD *)(v5 - 96) = *(v7 - 6);
            *(_OWORD *)(v5 - 80) = *(v7 - 5);
            *(_OWORD *)(v5 - 64) = *(v7 - 4);
            *(_OWORD *)(v5 - 48) = *(v7 - 3);
            *(_OWORD *)(v5 - 32) = *(v7 - 2);
            *(_OWORD *)(v5 - 16) = *(v7 - 1);
            --n6;
          }
          while ( n6 );
          *(_QWORD *)(a1 + 1208) = 0;
          return 1;
        }
      }
    }
    return 0;
  }
  return (unsigned int)sub_14309DE50(a1 + 88, v3) != 0;
}
