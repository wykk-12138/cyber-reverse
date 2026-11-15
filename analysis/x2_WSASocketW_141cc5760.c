/* x2 WSASocketW via cref @ 0x141cc5760 */
__int64 __fastcall sub_141CC5760(__int64 a1, int a2, int type, int protocol)
{
  __int64 result; // rax
  unsigned int v9; // r14d
  __int64 v10; // rbx

  *(_WORD *)(a1 + 106) = 257;
  *(_BYTE *)(a1 + 110) = 0;
  *(_DWORD *)(a1 + 100) = -1;
  result = sub_141CCF400(a2, type, protocol, (_QWORD *)(a1 + 8));
  v9 = result;
  if ( (_DWORD)result )
  {
    v10 = sub_143019310(&unk_144D9EAA0);
    sub_141CADAB0(v10, v9);
    sub_1430198D0(v10);
    __debugbreak();
  }
  *(_DWORD *)(a1 + 88) = a2;
  *(_DWORD *)(a1 + 92) = type;
  *(_DWORD *)(a1 + 96) = protocol;
  return result;
}
