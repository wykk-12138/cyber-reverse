/* entry 8 @ 0x1430e4850 */
_BOOL8 __fastcall BrotliDecoderHasMoreOutput(__int64 a1)
{
  return *(int *)(a1 + 128) >= 0
      && *(_QWORD *)(a1 + 136)
      && *(int *)(a1 + 88) + *(_QWORD *)(a1 + 424) * *(int *)(a1 + 100) - *(_QWORD *)(a1 + 432);
}
