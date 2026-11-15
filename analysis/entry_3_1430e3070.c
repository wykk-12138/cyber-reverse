/* entry 3 @ 0x1430e3070 */
__int64 __fastcall BrotliDecoderDecompress(__int64 a1, __int64 a2, __int64 *a3, __int64 a4)
{
  __int64 v4; // rax
  __int64 result; // rax
  int v7; // ebx
  __int64 v8; // [rsp+30h] [rbp-16C8h] BYREF
  __int64 v9; // [rsp+38h] [rbp-16C0h] BYREF
  __int64 v10; // [rsp+40h] [rbp-16B8h] BYREF
  __int64 v11; // [rsp+48h] [rbp-16B0h] BYREF
  __int64 v12; // [rsp+50h] [rbp-16A8h] BYREF
  _BYTE v13[5744]; // [rsp+60h] [rbp-1698h] BYREF

  v4 = *a3;
  v12 = a1;
  v11 = a2;
  v9 = a4;
  v8 = 0;
  v10 = v4;
  result = sub_1430EA170(v13, 0, 0, 0);
  if ( (_DWORD)result )
  {
    v7 = BrotliDecoderDecompressStream(
           (unsigned int)v13,
           (unsigned int)&v12,
           (unsigned int)&v11,
           (unsigned int)&v10,
           (__int64)&v9,
           (__int64)&v8);
    *a3 = v8;
    sub_1430E9F70(v13);
    return v7 == 1;
  }
  return result;
}
