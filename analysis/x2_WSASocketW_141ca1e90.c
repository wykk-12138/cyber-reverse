/* x2 WSASocketW via cref @ 0x141ca1e90 */
_BOOL8 sub_141CA1E90()
{
  bool v0; // bl
  _BOOL8 result; // rax

  v0 = sub_141CA1D40(23) && (unsigned int)sub_141CA1C90() == 0;
  if ( *((_QWORD *)&unk_14727A870 - 1) )
    sub_142F744B8();
  unk_14727A870 = v0;
  unk_14727A871 = sub_141CA1D40(2);
  result = sub_141CA1D40(1);
  unk_14727A872 = result;
  return result;
}
