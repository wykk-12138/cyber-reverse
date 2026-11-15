/* entry 1 @ 0x1430e2eb0 */
__int64 __fastcall BrotliDecoderAttachDictionary(__int64 a1)
{
  unsigned __int64 v2; // rdi
  unsigned int *v3; // rcx
  __int64 v4; // rsi
  __int64 v5; // rbp
  int *v6; // rax
  __int64 n15; // rcx
  __int64 v8; // r8
  int v9; // edx

  v2 = **(unsigned int **)(a1 + 800);
  if ( !*(_DWORD *)a1 && (unsigned int)BrotliSharedDictionaryAttach() )
  {
    v3 = *(unsigned int **)(a1 + 800);
    if ( v2 >= *v3 )
      return 1;
    while ( 1 )
    {
      v4 = *(_QWORD *)&v3[2 * v2 + 2];
      v5 = *(_QWORD *)&v3[2 * v2 + 32];
      v6 = *(int **)(a1 + 808);
      if ( *(_DWORD *)a1 )
        break;
      if ( !v6 )
      {
        v6 = (int *)(*(__int64 (__fastcall **)(_QWORD, __int64))(a1 + 48))(*(_QWORD *)(a1 + 64), 480);
        if ( !v6 )
          return 0;
        *(_QWORD *)v6 = 0;
        *((_QWORD *)v6 + 2) = 0;
        v6[54] = -1;
        v6[38] = 0;
        *(_QWORD *)(a1 + 808) = v6;
      }
      n15 = *v6;
      if ( (_DWORD)n15 == 15 )
        break;
      *(_QWORD *)&v6[2 * n15 + 6] = v5;
      ++v2;
      v6[1] += v4;
      v8 = *v6;
      v9 = v6[1];
      *v6 = v8 + 1;
      v6[v8 + 39] = v9;
      v3 = *(unsigned int **)(a1 + 800);
      if ( v2 >= *v3 )
        return 1;
    }
  }
  return 0;
}
