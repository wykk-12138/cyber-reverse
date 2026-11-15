/* entry 9 @ 0x1430e4890 */
_BOOL8 __fastcall BrotliDecoderIsFinished(__int64 a1)
{
  return *(_DWORD *)a1 == 26
      && (*(int *)(a1 + 128) < 0
       || !*(_QWORD *)(a1 + 136)
       || !(*(int *)(a1 + 88) + *(_QWORD *)(a1 + 424) * *(int *)(a1 + 100) - *(_QWORD *)(a1 + 432)));
}
