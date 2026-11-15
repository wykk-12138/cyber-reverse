/* entry 5 @ 0x1430e4640 */
__int64 __fastcall BrotliDecoderDestroyInstance(__int64 a1)
{
  __int64 v2; // rbx
  __int64 (__fastcall *v3)(__int64, __int64); // rdi
  __int64 result; // rax

  if ( a1 )
  {
    v2 = *(_QWORD *)(a1 + 64);
    v3 = *(__int64 (__fastcall **)(__int64, __int64))(a1 + 56);
    sub_1430E9F70(a1);
    return v3(v2, a1);
  }
  return result;
}
