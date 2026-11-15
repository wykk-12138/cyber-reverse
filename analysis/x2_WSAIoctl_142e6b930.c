/* x2 WSAIoctl via cref @ 0x142e6b930 */
__int64 __fastcall sub_142E6B930(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5)
{
  __int64 v8; // rdx
  __int64 v9; // rcx
  __int64 v11; // rbx
  DWORD lpcbBytesReturned_; // [rsp+48h] [rbp-40h] BYREF
  __int64 lpvOutBuffer_; // [rsp+50h] [rbp-38h] BYREF
  _BYTE lpvInBuffer[40]; // [rsp+58h] [rbp-30h] BYREF

  sub_141D15210(lpvInBuffer, a5);
  if ( (unsigned int)sub_141CC28D0(
                       a4,
                       0xC8000006,
                       lpvInBuffer,
                       0x10u,
                       &lpvOutBuffer_,
                       8u,
                       &lpcbBytesReturned_,
                       nullptr,
                       nullptr) )
  {
    v11 = sub_143019310(&unk_144D9EAA0);
    sub_141CADB20(v11);
    sub_1430198D0(v11);
    __debugbreak();
  }
  v8 = (*(__int64 (__fastcall **)(_QWORD, __int64))(a2 + 32))(*(_QWORD *)(a2 + 8), lpvOutBuffer_);
  if ( !a3 )
  {
    sub_141D24440(v9, v8);
    __debugbreak();
  }
  sub_143019660(a3, v8, 0);
  return *(_QWORD *)a3;
}
