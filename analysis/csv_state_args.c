==== state_arg2_builder ====
__int64 __fastcall sub_141D1FDF0(_QWORD *a1)
{
  *a1 = 0;
  a1[1] = 0;
  sub_143028EE0(a1);
  return sub_143028EE0(a1 + 1);
}


==== column_getter ====
_UNKNOWN **__fastcall sub_141CF6230(__int64 a1, __int64 a2)
{
  unsigned int v4; // edi
  int v5; // ebp
  int v6; // ebp
  __int64 v7; // rbp

  if ( a1 && (v4 = *(_DWORD *)(a1 + 8)) != 0 )
  {
    if ( a2 && (v5 = *(_DWORD *)(a2 + 8)) != 0 )
    {
      v6 = v4 + v5;
      if ( v6 < 0 )
      {
        sub_141D2DFB0();
        __debugbreak();
      }
      v7 = sub_143028CD0(&unk_144DB6A40, v6);
      sub_141CF5DD0(v7, 0, a1);
      sub_141CF5DD0(v7, v4, a2);
      return (_UNKNOWN **)v7;
    }
    else
    {
      return (_UNKNOWN **)a1;
    }
  }
  else if ( a2 && *(_DWORD *)(a2 + 8) )
  {
    return (_UNKNOWN **)a2;
  }
  else
  {
    return &off_146A622F8;
  }
}


