/* entry 2 @ 0x1430e2fc0 */
void *__fastcall BrotliDecoderCreateInstance(
        __int64 (__fastcall *a1)(__int64, __int64),
        void (__fastcall *a2)(__int64, void *),
        __int64 a3)
{
  void *v6; // rax
  void *v7; // rdi

  if ( !a1 )
  {
    if ( !a2 )
    {
      v6 = malloc(0x1670u);
      goto LABEL_6;
    }
    return nullptr;
  }
  if ( !a2 )
    return nullptr;
  v6 = (void *)a1(a3, 5744);
LABEL_6:
  v7 = v6;
  if ( !v6 )
    return nullptr;
  if ( !(unsigned int)sub_1430EA170(v6, a1, a2, a3) )
  {
    if ( a1 )
    {
      if ( a2 )
        a2(a3, v7);
    }
    else if ( !a2 )
    {
      free(v7);
    }
    return nullptr;
  }
  return v7;
}
