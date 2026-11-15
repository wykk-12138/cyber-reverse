/* x2 GetAddrInfoW via cref @ 0x141ca1f20 */
__int64 __fastcall sub_141CA1F20(
        __int64 a1,
        unsigned __int8 a2,
        int ai_family,
        __int64 a4,
        _QWORD *a5,
        _QWORD *a6,
        unsigned int *a7)
{
  unsigned int v11; // eax
  unsigned int v12; // r14d
  __int64 v13; // rax
  unsigned int v14; // esi
  PADDRINFOW ppResult_; // [rsp+20h] [rbp-68h] BYREF
  ADDRINFOW pHints_; // [rsp+28h] [rbp-60h] BYREF

  if ( !dword_1473E9DA4 )
    sub_141C9FF60();
  *a5 = &off_147219000;
  memset(&pHints_, 0, sizeof(pHints_));
  pHints_.ai_family = ai_family;
  if ( !a2 )
    pHints_.ai_flags = 2;
  ppResult_ = nullptr;
  v11 = sub_141C9FD60(a1, 0, &pHints_, &ppResult_);
  v12 = v11;
  if ( v11 )
  {
    *a7 = v11;
    sub_1430195E0(a4, a1);
    *a6 = &off_14721A868;
    v14 = v12;
  }
  else
  {
    v13 = sub_141CA2700(ppResult_, a2, a4);
    sub_1430195E0(a6, v13);
    *a7 = 0;
    v14 = 0;
  }
  if ( ppResult_ )
    sub_141C9FE60(ppResult_);
  return v14;
}
