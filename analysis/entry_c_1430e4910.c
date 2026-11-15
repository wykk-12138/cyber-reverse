/* entry 12 @ 0x1430e4910 */
__int64 __fastcall BrotliDecoderSetParameter(_DWORD *a1, int a2, int a3)
{
  int n16; // eax

  if ( *a1 )
    return 0;
  if ( a2 )
  {
    if ( a2 != 1 )
      return 0;
    a1[193] &= ~0x20u;
    a1[193] |= a3 != 0 ? 0x20 : 0;
    return 1;
  }
  else
  {
    a1[193] &= ~0x10u;
    n16 = 0;
    if ( !a3 )
      n16 = 16;
    a1[193] |= n16;
    return 1;
  }
}
