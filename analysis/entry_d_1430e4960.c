/* entry 13 @ 0x1430e4960 */
__int64 __fastcall BrotliDecoderTakeOutput(__int64 a1, __int64 *a2, __int64 a3)
{
  __int64 n0x1000000_1; // rax
  bool v4; // zf
  __int64 n0x1000000; // rbx
  int n2; // eax
  __int64 result; // rax
  __int64 n0x1000000_2; // [rsp+50h] [rbp+8h] BYREF
  __int64 v11; // [rsp+58h] [rbp+10h] BYREF

  n0x1000000_1 = *a2;
  v4 = *a2 == 0;
  v11 = 0;
  n0x1000000 = 0x1000000;
  if ( !v4 )
    n0x1000000 = n0x1000000_1;
  n0x1000000_2 = n0x1000000;
  if ( *(_QWORD *)(a1 + 136) && *(int *)(a1 + 128) >= 0 )
  {
    sub_1430E9470(a1, a2, a3);
    n2 = sub_1430E94B0(a1, (unsigned int)&n0x1000000_2, (unsigned int)&v11, 0, 1);
    if ( ((n2 - 1) & 0xFFFFFFFD) != 0 )
    {
      if ( n2 < 0 )
        sub_1430E92A0(a1, (unsigned int)n2, 0);
      *a2 = 0;
      return 0;
    }
    else
    {
      result = v11;
      *a2 = n0x1000000 - n0x1000000_2;
    }
  }
  else
  {
    *a2 = 0;
    return 0;
  }
  return result;
}
