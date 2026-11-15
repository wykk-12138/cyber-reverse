/* x2 WSASocketW via cref @ 0x141cc3540 */
_BOOL8 sub_141CC3540()
{
  bool v0; // bl
  _BOOL8 result; // rax

  v0 = sub_141CC33F0(23) && (unsigned int)sub_141CC3340() == 0;
  if ( *((_QWORD *)&unk_14727A928 - 1) )
    sub_142F744F8();
  unk_14727A928 = v0;
  unk_14727A929 = sub_141CC33F0(2);
  result = sub_141CC33F0(1);
  unk_14727A92A = result;
  return result;
}
