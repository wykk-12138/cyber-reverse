/* entry 4 @ 0x1430e3140 */
__int64 __fastcall BrotliDecoderDecompressStream(
        __int64 a1,
        __int64 *a2,
        _QWORD *a3,
        _QWORD *a4,
        _QWORD *a5,
        _QWORD *a6)
{
  _QWORD *v6; // r10
  __int64 *v7; // r13
  __int64 v8; // rdx
  _QWORD *v9; // r12
  _BYTE **v10; // rdi
  unsigned int n2; // esi
  _QWORD *v14; // r11
  __int64 v15; // rax
  __int64 v16; // rdx
  _BYTE *v17; // r8
  bool v18; // zf
  _BYTE *v19; // rax
  __int64 v20; // rcx
  __int64 v21; // rdx
  unsigned __int64 n6; // r8
  unsigned __int64 n0x40_1; // rdx
  _QWORD *v24; // r15
  int n2_1; // eax
  __int64 v26; // rdx
  __int64 v27; // rdx
  _BYTE *v28; // r8
  _BYTE *v29; // rax
  __int64 v30; // rcx
  __int64 v31; // rax
  __int64 v32; // rdx
  __int64 v33; // rcx
  int v34; // r8d
  __int64 v35; // rcx
  __int64 v36; // rax
  unsigned __int64 v37; // rdx
  __int64 v38; // rax
  __int64 v39; // rcx
  unsigned __int64 v40; // rdx
  unsigned int v41; // ecx
  __int64 v42; // rax
  __int64 v43; // rcx
  unsigned __int64 v44; // rdx
  unsigned __int8 *v45; // r9
  unsigned __int8 *v46; // rdx
  unsigned __int64 v47; // rax
  __int64 v48; // rcx
  __int16 v49; // dx
  __int64 v50; // rcx
  __int64 v51; // rax
  unsigned int n2_3; // eax
  _BYTE *v53; // r11
  unsigned __int64 v54; // rcx
  unsigned __int64 v55; // rax
  _BYTE *v56; // r9
  void (__fastcall *v57)(_QWORD, _QWORD, unsigned __int64); // rax
  _BYTE *v58; // r11
  __int64 n3; // rax
  unsigned int n2_4; // eax
  __int64 v61; // rcx
  __int64 v62; // rdx
  __int64 v63; // r8
  __int64 n26; // rdx
  unsigned int n2_5; // eax
  unsigned int n2_6; // eax
  __int64 v67; // rdx
  __int64 v68; // rdi
  __int64 v69; // r11
  unsigned __int64 n0xF; // r8
  unsigned __int8 *v71; // r9
  unsigned __int8 *v72; // rdx
  unsigned __int64 v73; // rax
  unsigned __int64 v74; // r9
  unsigned __int64 v75; // r10
  unsigned __int8 *v76; // r11
  int n8; // eax
  __int64 v78; // r10
  unsigned __int64 v79; // r9
  unsigned __int64 v80; // rcx
  __int64 v81; // r11
  unsigned __int8 *v82; // r8
  unsigned __int8 *v83; // rdx
  unsigned __int64 v84; // rax
  unsigned __int64 v85; // rdx
  __int64 v86; // rax
  __int64 v87; // rax
  unsigned int n2_11; // eax
  unsigned int n2_12; // eax
  unsigned __int64 n6_1; // r8
  unsigned __int8 *v91; // r9
  unsigned __int8 *v92; // rdx
  unsigned __int64 v93; // rax
  unsigned __int64 v94; // rdx
  unsigned __int64 v95; // rcx
  __int64 (__fastcall *v96)(__int64, _QWORD); // rax
  unsigned __int64 v97; // rdx
  __int64 v98; // rcx
  __int64 v99; // rax
  int v100; // r10d
  __int64 v101; // r11
  unsigned __int64 n2_7; // r8
  unsigned __int8 *v103; // r9
  unsigned __int8 *v104; // rdx
  unsigned __int64 v105; // rax
  unsigned __int64 v106; // rcx
  unsigned int n2_8; // eax
  unsigned __int64 v108; // rdi
  __int64 v109; // r11
  unsigned __int64 n0x40_2; // r10
  __int64 v111; // r9
  __int64 v112; // r8
  __int64 v113; // rdx
  __int64 v114; // rcx
  __int64 v115; // r11
  __int64 n0x7FFFFFFC; // r9
  int n256; // r15d
  int n256_1; // ebp
  int v119; // edx
  unsigned int i; // eax
  unsigned int v121; // r8d
  unsigned int n2_9; // eax
  unsigned __int8 v123; // si
  char v124; // di
  int v125; // ecx
  int v126; // ecx
  __int64 n184; // r15
  _QWORD *v128; // rdi
  __int64 v129; // rax
  int v130; // ecx
  int n3_1; // eax
  unsigned __int64 v132; // r9
  unsigned __int8 *v133; // r8
  __int64 v134; // rax
  __int64 v135; // rcx
  __int64 v136; // rax
  unsigned __int64 v137; // rcx
  _QWORD *v138; // rax
  __int64 v139; // r12
  __int64 v140; // r11
  __int64 v141; // r13
  unsigned __int64 n0x40_3; // r15
  char v143; // r9
  __int64 v144; // rbp
  _BYTE *v145; // rcx
  __int64 v146; // r10
  unsigned __int64 v147; // rcx
  unsigned int n2_10; // eax
  unsigned int n2_13; // eax
  __int64 v150; // rcx
  unsigned int v151; // edi
  int v152; // eax
  int v153; // ecx
  int n14; // eax
  int n14_1; // eax
  unsigned __int64 n0x40_4; // r8
  __int64 v157; // rdx
  unsigned __int64 v158; // rcx
  unsigned __int64 v159; // rax
  unsigned __int64 v160; // r9
  unsigned __int64 n0x40_5; // r8
  __int64 n2_2; // rdx
  __int64 v163; // rax
  __int64 v164; // r8
  __int64 v165; // rdx
  unsigned __int64 n0x40; // rcx
  __int64 v167; // [rsp+30h] [rbp-68h]
  __int64 v168; // [rsp+38h] [rbp-60h] BYREF
  __int64 v169[3]; // [rsp+40h] [rbp-58h] BYREF
  _QWORD *v170; // [rsp+A0h] [rbp+8h]

  v6 = a6;
  v7 = a2;
  v8 = *a2;
  v167 = v8;
  v9 = a4;
  v10 = (_BYTE **)a3;
  n2 = 1;
  if ( a6 )
    *a6 = *(_QWORD *)(a1 + 432);
  if ( *(int *)(a1 + 128) < 0 )
    return 0;
  if ( *a4 && (!a5 || !*a5) )
    return sub_1430E92A0(a1, 4294967276LL, v8 - *v7);
  v14 = nullptr;
  if ( *a4 )
    v14 = a5;
  v15 = *(_QWORD *)(a1 + 80);
  v170 = v14;
  if ( v15 )
  {
    v20 = a1 + 72;
    n2 = 2;
    v21 = v15 + a1 + 72;
    *(_QWORD *)(a1 + 24) = a1 + 72;
    *(_QWORD *)(a1 + 40) = v21;
    if ( (unsigned __int64)(v15 + 1) > 0x1C )
      v20 = v21 - 27;
  }
  else
  {
    v16 = *v7;
    v17 = (_BYTE *)*a3;
    v18 = *v7 == 0;
    v19 = v17;
    *(_QWORD *)(a1 + 24) = v17;
    if ( !v18 )
      v19 = &v17[v16];
    v20 = (__int64)&v17[v16 - 27];
    *(_QWORD *)(a1 + 40) = v19;
    if ( (unsigned __int64)(v16 + 1) <= 0x1C )
      v20 = (__int64)v17;
  }
  *(_QWORD *)(a1 + 32) = v20;
  n6 = 0x140000000uLL;
  n0x40_1 = 2147483660LL;
LABEL_20:
  v24 = (_QWORD *)(a1 + 784);
  while ( 2 )
  {
    while ( n2 != 1 )
    {
      if ( n2 != 2 )
      {
        if ( *(_QWORD *)(a1 + 80) )
        {
          *(_QWORD *)(a1 + 80) = 0;
        }
        else
        {
          v164 = *(_QWORD *)(a1 + 24);
          v165 = *(_QWORD *)(a1 + 16) >> 3;
          if ( v165 )
            v164 = *(_QWORD *)(a1 + 24) - v165;
          n0x40 = *(_QWORD *)(a1 + 16) - 8 * v165;
          *(_QWORD *)(a1 + 24) = v164;
          *(_QWORD *)(a1 + 16) = n0x40;
          if ( n0x40 < 0x40 )
            *(_QWORD *)(a1 + 8) &= (1LL << n0x40) - 1;
          *v7 = *(_QWORD *)(a1 + 40) - v164;
          *v10 = *(_BYTE **)(a1 + 24);
        }
        goto LABEL_220;
      }
      if ( *(_QWORD *)(a1 + 136) )
      {
        n2_1 = sub_1430E94B0(a1, (_DWORD)v9, (_DWORD)v14, (_DWORD)v6, 1);
        if ( n2_1 < 0 )
        {
          n2 = n2_1;
LABEL_220:
          n2_2 = n2;
          return sub_1430E92A0(a1, n2_2, v167 - *v7);
        }
        v6 = a6;
        v14 = v170;
      }
      v26 = *(_QWORD *)(a1 + 80);
      if ( !v26 )
      {
        *v10 = *(_BYTE **)(a1 + 24);
        v163 = *(_QWORD *)(a1 + 40) - *(_QWORD *)(a1 + 24);
        *v7 = v163;
        if ( v163 )
        {
          do
          {
            *(_BYTE *)(*(_QWORD *)(a1 + 80) + a1 + 72) = **v10;
            ++*(_QWORD *)(a1 + 80);
            ++*v10;
            v18 = (*v7)-- == 1;
          }
          while ( !v18 );
        }
        goto LABEL_220;
      }
      if ( *(_QWORD *)(a1 + 24) == *(_QWORD *)(a1 + 40) )
      {
        *(_QWORD *)(a1 + 80) = 0;
        n2 = 1;
        v27 = *v7;
        v28 = *v10;
        v18 = *v7 == 0;
        v29 = *v10;
        *(_QWORD *)(a1 + 24) = *v10;
        if ( !v18 )
          v29 = &v28[v27];
        v30 = (__int64)&v28[v27 - 27];
        *(_QWORD *)(a1 + 40) = v29;
        if ( (unsigned __int64)(v27 + 1) <= 0x1C )
          v30 = (__int64)v28;
        *(_QWORD *)(a1 + 32) = v30;
      }
      else
      {
        if ( !*v7 )
          goto LABEL_220;
        n2 = 1;
        v31 = a1 + 72;
        *(_BYTE *)(v26 + a1 + 72) = **v10;
        v18 = (*(_QWORD *)(a1 + 80))++ == -1;
        v32 = *(_QWORD *)(a1 + 80);
        *(_QWORD *)(a1 + 24) = a1 + 72;
        if ( !v18 )
          v31 = v32 + a1 + 72;
        v33 = v32 + a1 + 72 - 27;
        *(_QWORD *)(a1 + 40) = v31;
        if ( (unsigned __int64)(v32 + 1) <= 0x1C )
          v33 = a1 + 72;
        *(_QWORD *)(a1 + 32) = v33;
        ++*v10;
        --*v7;
      }
LABEL_218:
      n6 = 0x140000000uLL;
      n0x40_1 = 2147483660LL;
    }
    switch ( *(_DWORD *)a1 )
    {
      case 0:
        if ( !(unsigned int)sub_1430E95F0(a1 + 8, 2147483660LL, 0x140000000uLL) )
        {
          n2 = 2;
          goto LABEL_216;
        }
        v34 = *(_DWORD *)(a1 + 772);
        *(_DWORD *)(a1 + 772) = v34 & 0xFFFFFFDF;
        v35 = *(_QWORD *)(a1 + 8) & 1LL;
        v36 = *(_QWORD *)(a1 + 16) - 1LL;
        v37 = *(_QWORD *)(a1 + 8) >> 1;
        *(_QWORD *)(a1 + 16) = v36;
        *(_QWORD *)(a1 + 8) = v37;
        if ( !v35 )
        {
          *(_DWORD *)(a1 + 772) &= 0xFFFFF43F;
          n2 = 1;
          *(_DWORD *)(a1 + 772) |= 0x400u;
          *(_DWORD *)a1 = 2 - ((*(_DWORD *)(a1 + 772) & 0x20) != 0);
          goto LABEL_216;
        }
        v38 = v36 - 3;
        v39 = v37 & 7;
        v40 = v37 >> 3;
        *(_QWORD *)(a1 + 16) = v38;
        *(_QWORD *)(a1 + 8) = v40;
        if ( v39 )
        {
          v41 = *(_DWORD *)(a1 + 772)
              ^ ((unsigned __int16)*(_DWORD *)(a1 + 772)
               ^ (unsigned __int16)(((_WORD)v39 + 17) << 6))
              & 0xFC0;
        }
        else
        {
          v42 = v38 - 3;
          v43 = v40 & 7;
          v44 = v40 >> 3;
          *(_QWORD *)(a1 + 16) = v42;
          *(_QWORD *)(a1 + 8) = v44;
          if ( v43 == 1 )
          {
            if ( (v34 & 0x20) != 0 && (*(_QWORD *)(a1 + 8) = v44 >> 1, *(_QWORD *)(a1 + 16) = v42 - 1, (v44 & 1) != 1) )
            {
              *(_DWORD *)(a1 + 772) |= 0x20u;
              n2 = 1;
              *(_DWORD *)a1 = 2 - ((*(_DWORD *)(a1 + 772) & 0x20) != 0);
            }
            else
            {
              n2 = -13;
            }
            goto LABEL_216;
          }
          if ( v43 )
            v41 = *(_DWORD *)(a1 + 772)
                ^ ((unsigned __int16)*(_DWORD *)(a1 + 772)
                 ^ (unsigned __int16)(((_WORD)v43 + 8) << 6))
                & 0xFC0;
          else
            v41 = *(_DWORD *)(a1 + 772) & 0xFFFFF03F | 0x440;
        }
        *(_DWORD *)(a1 + 772) = v41;
        n2 = 1;
        *(_DWORD *)a1 = 2 - ((v41 & 0x20) != 0);
        goto LABEL_216;
      case 1:
        n6 = *(_QWORD *)(a1 + 16);
        if ( n6 >= 6 )
          goto LABEL_59;
        v45 = *(unsigned __int8 **)(a1 + 40);
        do
        {
          v46 = *(unsigned __int8 **)(a1 + 24);
          if ( v46 == v45 )
            goto LABEL_63;
          v47 = (unsigned __int64)*v46 << n6;
          n6 += 8LL;
          *(_QWORD *)(a1 + 8) |= v47;
          *(_QWORD *)(a1 + 24) = v46 + 1;
          *(_QWORD *)(a1 + 16) = n6;
        }
        while ( n6 < 6 );
LABEL_59:
        v48 = *(_QWORD *)(a1 + 8) >> 6;
        v49 = *(_QWORD *)(a1 + 8) & 0x3F;
        *(_QWORD *)(a1 + 16) = n6 - 6;
        *(_QWORD *)(a1 + 8) = v48;
        *(_DWORD *)(a1 + 772) ^= ((unsigned __int16)*(_DWORD *)(a1 + 772) ^ (unsigned __int16)(v49 << 6)) & 0xFC0;
        if ( (v49 & 0x3Fu) - 10 > 0x14 )
        {
          n2 = -13;
          goto LABEL_218;
        }
        *(_DWORD *)a1 = 2;
LABEL_61:
        v50 = *(_QWORD *)(a1 + 64);
        *(_DWORD *)(a1 + 92) = (1 << ((*(_DWORD *)(a1 + 772) >> 6) & 0x3F)) - 16;
        v51 = (*(__int64 (__fastcall **)(__int64, __int64, unsigned __int64))(a1 + 48))(v50, 12336, n6);
        *(_QWORD *)(a1 + 256) = v51;
        if ( !v51 )
        {
          n2 = -30;
          goto LABEL_216;
        }
        *(_DWORD *)a1 = 3;
        *(_QWORD *)(a1 + 264) = v51 + 7584;
LABEL_66:
        sub_1430EA310(a1, n0x40_1, n6);
        *(_DWORD *)a1 = 4;
LABEL_67:
        n2_3 = sub_1430E5900(a1, a1 + 8, n6);
        v6 = a6;
        n2 = n2_3;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_3 != 1 )
          continue;
        v53 = (_BYTE *)(a1 + 772);
        if ( (*(_BYTE *)(a1 + 772) & 6) != 0 )
        {
          n0x40_1 = *(_QWORD *)(a1 + 16);
          n6 = 0;
          v54 = n0x40_1 & 7;
          if ( (n0x40_1 & 7) != 0 )
          {
            v55 = *(_QWORD *)(a1 + 8);
            n0x40_1 -= v54;
            n6 = v55 & qword_1462B79A0[v54];
            *(_QWORD *)(a1 + 16) = n0x40_1;
            v56 = (_BYTE *)(a1 + 772);
            *(_QWORD *)(a1 + 8) = v55 >> v54;
          }
          else
          {
            v56 = (_BYTE *)(a1 + 772);
          }
          if ( n0x40_1 < 0x40 )
          {
            v53 = v56;
            *(_QWORD *)(a1 + 8) &= (1LL << n0x40_1) - 1;
          }
          if ( n6 )
          {
            n2 = -14;
            goto LABEL_217;
          }
        }
        if ( (*v53 & 4) != 0 )
        {
          v57 = *(void (__fastcall **)(_QWORD, _QWORD, unsigned __int64))(a1 + 720);
          n6 = 0x140000000uLL;
          v14 = v170;
          n0x40_1 = 2147483660LL;
          *(_DWORD *)a1 = 12;
          if ( !v57 )
            continue;
          v57(*(_QWORD *)(a1 + 736), *(int *)(a1 + 132), 0x140000000uLL);
          goto LABEL_216;
        }
        if ( !*(_DWORD *)(a1 + 132) )
        {
          *(_DWORD *)a1 = 14;
          goto LABEL_217;
        }
        sub_1430E2E30(a1, n0x40_1, n6);
        if ( (*v58 & 2) != 0 )
        {
          *(_DWORD *)a1 = 11;
          goto LABEL_216;
        }
        v6 = a6;
        n6 = 0x140000000uLL;
        v14 = v170;
        n0x40_1 = 2147483660LL;
LABEL_84:
        *(_QWORD *)a1 = 18;
        *(_QWORD *)(a1 + 1040) = a1 + 1080;
        *(_QWORD *)(a1 + 864) = 0;
        *(_QWORD *)(a1 + 852) = 0;
        *(_DWORD *)(a1 + 848) = 0;
LABEL_85:
        n3 = *(int *)(a1 + 4);
        if ( (int)n3 >= 3 )
        {
          *(_DWORD *)a1 = 5;
          continue;
        }
        n2_4 = sub_1430E5EC0(a1, a1 + 8, a1 + 8 * (n3 + 39));
        v6 = a6;
        n2 = n2_4;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_4 != 1 )
          continue;
        ++*(_QWORD *)(a1 + 8LL * *(int *)(a1 + 4) + 312);
        v61 = *(int *)(a1 + 4);
        if ( *(_QWORD *)(a1 + 8 * v61 + 312) < 2u )
        {
          *(_DWORD *)(a1 + 4) = v61 + 1;
          n6 = 0x140000000uLL;
          continue;
        }
        *(_DWORD *)a1 = 19;
LABEL_91:
        v62 = *(int *)(a1 + 4);
        v63 = *(_QWORD *)(a1 + 256) + 2528LL * (_DWORD)v62;
        n26 = *(_QWORD *)(a1 + 8 * v62 + 312) + 2LL;
        n2_5 = sub_1430E6DD0(n26, n26, v63, 0, a1);
        v6 = a6;
        n2 = n2_5;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_5 != 1 )
          continue;
        *(_DWORD *)a1 = 20;
LABEL_93:
        n2_6 = sub_1430E6DD0(26, 26, *(_QWORD *)(a1 + 264) + 1584LL * *(_DWORD *)(a1 + 4), 0, a1);
        v6 = a6;
        n2 = n2_6;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_6 != 1 )
          continue;
        *(_DWORD *)a1 = 21;
        n6 = 0x140000000uLL;
LABEL_95:
        v67 = *(int *)(a1 + 4);
        v68 = a1 + 8 * v67;
        v69 = *(_QWORD *)(a1 + 264) + 1584LL * (_DWORD)v67;
        if ( *(_DWORD *)(a1 + 764) )
        {
          v78 = *(_QWORD *)(a1 + 304);
          v168 = v78;
        }
        else
        {
          n0xF = *(_QWORD *)(a1 + 16);
          if ( n0xF >= 0xF )
          {
LABEL_100:
            v74 = *(_QWORD *)(a1 + 8);
            v75 = v74 & 0x7FFF;
            v76 = (unsigned __int8 *)(v69 + 4LL * *(unsigned __int8 *)(a1 + 8));
            n8 = *v76;
            if ( (unsigned __int8)n8 > 8u )
            {
              v74 >>= 8;
              *(_QWORD *)(a1 + 8) = v74;
              n0xF -= 8LL;
              *(_QWORD *)(a1 + 16) = n0xF;
              v76 += 4 * *((unsigned __int16 *)v76 + 1) + 4 * ((v75 >> 8) & qword_1462B79A0[n8 - 8]);
              LOBYTE(n8) = *v76;
            }
            *(_QWORD *)(a1 + 16) = n0xF - (unsigned __int8)n8;
            n6 = 0x140000000uLL;
            *(_QWORD *)(a1 + 8) = v74 >> n8;
            v78 = *((unsigned __int16 *)v76 + 1);
            v168 = v78;
          }
          else
          {
            v71 = *(unsigned __int8 **)(a1 + 40);
            while ( 1 )
            {
              v72 = *(unsigned __int8 **)(a1 + 24);
              if ( v72 == v71 )
                break;
              v73 = (unsigned __int64)*v72 << n0xF;
              n0xF += 8LL;
              *(_QWORD *)(a1 + 8) |= v73;
              *(_QWORD *)(a1 + 24) = v72 + 1;
              *(_QWORD *)(a1 + 16) = n0xF;
              if ( n0xF >= 0xF )
                goto LABEL_100;
            }
            if ( !(unsigned int)sub_1430E81C0(v69, a1 + 8, &v168) )
            {
LABEL_113:
              v10 = (_BYTE **)a3;
              n2 = 2;
              goto LABEL_216;
            }
            v78 = v168;
            n6 = 0x140000000uLL;
          }
        }
        v79 = (unsigned __int8)byte_1462DEB62[4 * v78];
        v80 = *(_QWORD *)(a1 + 16);
        v81 = (unsigned __int16)kBrotliPrefixCodeRanges[2 * v78];
        if ( v80 >= v79 )
        {
LABEL_111:
          v85 = *(_QWORD *)(a1 + 8);
          v6 = a6;
          v86 = v85 & qword_1462B79A0[v79];
          *(_QWORD *)(a1 + 16) = v80 - v79;
          v87 = v81 + v86;
          v14 = v170;
          *(_QWORD *)(a1 + 8) = v85 >> v79;
          n0x40_1 = 2147483660LL;
          *(_QWORD *)(v68 + 280) = v87;
          ++*(_DWORD *)(a1 + 4);
          v10 = (_BYTE **)a3;
          *(_DWORD *)(a1 + 764) = 0;
          *(_DWORD *)a1 = 18;
          continue;
        }
        v82 = *(unsigned __int8 **)(a1 + 40);
        while ( 1 )
        {
          v83 = *(unsigned __int8 **)(a1 + 24);
          if ( v83 == v82 )
            break;
          v84 = (unsigned __int64)*v83 << v80;
          v80 += 8LL;
          *(_QWORD *)(a1 + 8) |= v84;
          *(_QWORD *)(a1 + 24) = v83 + 1;
          *(_QWORD *)(a1 + 16) = v80;
          if ( v80 >= v79 )
          {
            n6 = 0x140000000uLL;
            goto LABEL_111;
          }
        }
        *(_QWORD *)(a1 + 304) = v78;
        *(_DWORD *)(a1 + 764) = 1;
        goto LABEL_113;
      case 2:
        goto LABEL_61;
      case 3:
        goto LABEL_66;
      case 4:
        goto LABEL_67;
      case 5:
        n6_1 = *(_QWORD *)(a1 + 16);
        if ( n6_1 >= 6 )
          goto LABEL_122;
        v91 = *(unsigned __int8 **)(a1 + 40);
        do
        {
          v92 = *(unsigned __int8 **)(a1 + 24);
          if ( v92 == v91 )
          {
LABEL_63:
            n2 = 2;
            goto LABEL_218;
          }
          v93 = (unsigned __int64)*v92 << n6_1;
          n6_1 += 8LL;
          *(_QWORD *)(a1 + 8) |= v93;
          *(_QWORD *)(a1 + 24) = v92 + 1;
          *(_QWORD *)(a1 + 16) = n6_1;
        }
        while ( n6_1 < 6 );
LABEL_122:
        v94 = *(_QWORD *)(a1 + 8) & 0x3FLL;
        *(_QWORD *)(a1 + 8) >>= 6;
        *(_QWORD *)(a1 + 16) = n6_1 - 6;
        v95 = v94 & 3;
        v96 = *(__int64 (__fastcall **)(__int64, _QWORD))(a1 + 48);
        v97 = v94 >> 2 << v95;
        *(_QWORD *)(a1 + 384) = v95;
        v98 = *(_QWORD *)(a1 + 64);
        *(_QWORD *)(a1 + 392) = v97;
        v99 = v96(v98, *(_QWORD *)(a1 + 312));
        *(_QWORD *)(a1 + 792) = v99;
        if ( !v99 )
        {
          n2 = -21;
          goto LABEL_216;
        }
        *(_QWORD *)a1 = 6;
LABEL_125:
        v100 = *(_DWORD *)(a1 + 4);
        if ( v100 < *(_DWORD *)(a1 + 312) )
        {
          v101 = *(int *)(a1 + 4);
          while ( 1 )
          {
            n2_7 = *(_QWORD *)(a1 + 16);
            if ( n2_7 < 2 )
              break;
LABEL_131:
            v106 = *(_QWORD *)(a1 + 8);
            ++v100;
            *(_QWORD *)(a1 + 16) = n2_7 - 2;
            *(_QWORD *)(a1 + 8) = v106 >> 2;
            *(_BYTE *)(v101 + *(_QWORD *)(a1 + 792)) = v106 & 3;
            ++v101;
            if ( v100 >= *(_DWORD *)(a1 + 312) )
              goto LABEL_132;
          }
          v103 = *(unsigned __int8 **)(a1 + 40);
          while ( 1 )
          {
            v104 = *(unsigned __int8 **)(a1 + 24);
            if ( v104 == v103 )
              break;
            v105 = (unsigned __int64)*v104 << n2_7;
            n2_7 += 8LL;
            *(_QWORD *)(a1 + 8) |= v105;
            *(_QWORD *)(a1 + 24) = v104 + 1;
            *(_QWORD *)(a1 + 16) = n2_7;
            if ( n2_7 >= 2 )
              goto LABEL_131;
          }
          *(_DWORD *)(a1 + 4) = v100;
          n2 = 2;
LABEL_216:
          v6 = a6;
LABEL_217:
          v14 = v170;
          goto LABEL_218;
        }
LABEL_132:
        *(_DWORD *)a1 = 22;
LABEL_133:
        n2_8 = sub_1430E4FD0(*(_QWORD *)(a1 + 312) << 6);
        v6 = a6;
        n2 = n2_8;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_8 != 1 )
          continue;
        *(_QWORD *)(a1 + 816) = 0;
        v108 = 0;
        *(_QWORD *)(a1 + 824) = 0;
        *(_QWORD *)(a1 + 832) = 0;
        for ( *(_QWORD *)(a1 + 840) = 0; v108 < *(_QWORD *)(a1 + 312); ++v108 )
        {
          v109 = 0;
          n0x40_2 = 0;
          v112 = *v24 + (v108 << 6) + 2;
          do
          {
            v113 = *(unsigned __int8 *)(*v24 + (v108 << 6) + n0x40_2);
            n0x40_2 += 4LL;
            v114 = *(unsigned __int8 *)(v112 - 1);
            v112 += 4;
            v111 = *(unsigned __int8 *)(*v24 + (v108 << 6));
            v109 |= v111 ^ *(unsigned __int8 *)(v112 - 4)
                  | v111 ^ *(unsigned __int8 *)(v112 - 3)
                  | v111 ^ v114
                  | v111 ^ v113;
          }
          while ( n0x40_2 < 0x40 );
          if ( !v109 )
            *(_DWORD *)(a1 + 4 * (v108 >> 5) + 816) |= 1 << (v108 & 0x1F);
        }
        v10 = (_BYTE **)a3;
        *(_DWORD *)a1 = 23;
LABEL_142:
        v115 = *(_QWORD *)(a1 + 384);
        n0x7FFFFFFC = *(_QWORD *)(a1 + 392);
        n256 = (24 << (v115 + 1)) + n0x7FFFFFFC + 16;
        n256_1 = n256;
        if ( (*(_BYTE *)(a1 + 772) & 0x20) != 0 )
        {
          if ( (unsigned int)n0x7FFFFFFC < 0x7FFFFFFC )
          {
            v119 = 0;
            for ( i = (((unsigned int)(2147483644 - n0x7FFFFFFC) >> v115) + 4) >> 1; i; i >>= 1 )
              ++v119;
            v121 = (2 * v119 - 4) | ((((unsigned int)(2147483644 - n0x7FFFFFFC) >> v115) + 4) >> (v119 - 1)) & 1;
            if ( v121 )
              n256_1 = n0x7FFFFFFC + (((1 << v115) - 1) | ((v121 - 1) << v115)) + 17;
            else
              n256_1 = n0x7FFFFFFC + 16;
          }
          else
          {
            n256_1 = -2147483636;
          }
          n256 = n0x7FFFFFFC + (62 << (v115 + 1)) + 16;
        }
        n2_9 = sub_1430E4FD0(4LL * *(_QWORD *)(a1 + 328));
        v6 = a6;
        n2 = n2_9;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_9 != 1 )
        {
          v9 = a4;
          goto LABEL_20;
        }
        v123 = sub_1430E9EF0(a1, (int)a1 + 184, 256, 256, *(_QWORD *)(a1 + 776));
        v124 = sub_1430E9EF0(a1, (int)a1 + 208, 704, 704, *(_QWORD *)(a1 + 320));
        if ( (v123 & (unsigned __int8)(v124 & sub_1430E9EF0(a1, (int)a1 + 232, n256, n256_1, *(_QWORD *)(a1 + 400))) & 1) == 0 )
        {
          n2_2 = 4294967274LL;
          return sub_1430E92A0(a1, n2_2, v167 - *v7);
        }
        *(_QWORD *)a1 = 24;
LABEL_154:
        v125 = *(_DWORD *)(a1 + 4);
        if ( !v125 )
        {
          n184 = 184;
LABEL_160:
          v128 = (_QWORD *)(a1 + 2672);
          if ( *(_DWORD *)(a1 + 848) != 1 )
          {
            *v128 = *(_QWORD *)(n184 + a1 + 8);
            *(_DWORD *)(a1 + 2668) = 0;
            *(_DWORD *)(a1 + 848) = 1;
          }
          if ( *(_DWORD *)(a1 + 2668) < (int)*(unsigned __int16 *)(n184 + a1 + 20) )
          {
            while ( 1 )
            {
              n2 = sub_1430E6DD0(
                     *(unsigned __int16 *)(n184 + a1 + 16),
                     *(unsigned __int16 *)(n184 + a1 + 18),
                     *v128,
                     v169,
                     a1);
              if ( n2 != 1 )
                break;
              *(_QWORD *)(*(_QWORD *)(n184 + a1) + 8LL * *(int *)(a1 + 2668)) = *v128;
              v129 = v169[0];
              v130 = *(_DWORD *)(a1 + 2668) + 1;
              *(_DWORD *)(a1 + 2668) = v130;
              *v128 += 4 * v129;
              if ( v130 >= *(unsigned __int16 *)(n184 + a1 + 20) )
                goto LABEL_165;
            }
            v10 = (_BYTE **)a3;
            v24 = (_QWORD *)(a1 + 784);
            v9 = a4;
            goto LABEL_216;
          }
LABEL_165:
          v10 = (_BYTE **)a3;
          v24 = (_QWORD *)(a1 + 784);
          v6 = a6;
          n6 = 0x140000000uLL;
          v14 = v170;
          n2 = 1;
          v9 = a4;
          n0x40_1 = 2147483660LL;
          *(_DWORD *)(a1 + 848) = 0;
          n3_1 = *(_DWORD *)(a1 + 4) + 1;
          *(_DWORD *)(a1 + 4) = n3_1;
          if ( n3_1 >= 3 )
          {
            *(_DWORD *)a1 = 25;
            v24 = (_QWORD *)(a1 + 784);
LABEL_167:
            v132 = *(_QWORD *)(a1 + 344);
            v133 = (unsigned __int8 *)(*v24 + (v132 << 6));
            *(_QWORD *)(a1 + 168) = v133;
            v134 = *(_QWORD *)(a1 + 184);
            *(_DWORD *)(a1 + 272) = (*(unsigned int *)(a1 + 4 * (v132 >> 5) + 816) >> (v132 & 0x1F)) & 1;
            v135 = *(_QWORD *)(v134 + 8LL * *v133);
            v136 = *(_QWORD *)(a1 + 792);
            *(_QWORD *)(a1 + 416) = v135;
            v137 = (unsigned __int64)(*(_BYTE *)(v136 + v132) & 3) << 9;
            *(_QWORD *)(a1 + 176) = *(_QWORD *)(a1 + 408);
            v138 = *(_QWORD **)(a1 + 208);
            *(_QWORD *)(a1 + 160) = (char *)&kBrotliContextLookupTable + v137;
            *(_QWORD *)(a1 + 152) = *v138;
            if ( !(unsigned int)sub_1430E4A30(a1) )
            {
              v9 = a4;
              n2 = -27;
              goto LABEL_216;
            }
            v139 = *(_QWORD *)(a1 + 384);
            v140 = a1 + 848;
            v141 = *(_QWORD *)(a1 + 392);
            n0x40_3 = *(unsigned __int16 *)(a1 + 250);
            v143 = 1;
            v144 = 0;
            n0x40_1 = 16;
            if ( v141 )
            {
              v145 = (_BYTE *)(a1 + 864);
              n6 = a1 + 1520;
              v146 = *(_QWORD *)(a1 + 392);
              n0x40_1 = v141 + 16;
              do
              {
                *v145 = 0;
                *(_QWORD *)n6 = &v145[-15 - v140];
                n6 += 8LL;
                ++v145;
                --v146;
              }
              while ( v146 );
            }
            for ( ; n0x40_1 < n0x40_3; v144 ^= 1uLL )
            {
              n6 = a1 + 1392 + 8 * n0x40_1;
              v147 = 0;
              do
              {
                *(_BYTE *)(n0x40_1 + v140) = v143;
                ++n0x40_1;
                *(_QWORD *)n6 = v141 + ((((v144 + 2) << v143) - 4) << v139) + 1 + v147++;
                n6 += 8LL;
              }
              while ( v147 < 1LL << v139 );
              v143 += v144;
            }
            v7 = a2;
            v10 = (_BYTE **)a3;
            *(_DWORD *)a1 = 7;
LABEL_178:
            n2_10 = sub_1430E6280(a1, n0x40_1, n6);
            v6 = a6;
            n2 = n2_10;
            v14 = v170;
            v9 = a4;
            v24 = (_QWORD *)(a1 + 784);
            n6 = 0x140000000uLL;
            n0x40_1 = 2147483660LL;
            if ( n2_10 == 2 )
            {
              n2 = sub_1430E8260(a1, 2147483660LL, 0x140000000uLL);
              v24 = (_QWORD *)(a1 + 784);
              goto LABEL_216;
            }
          }
          continue;
        }
        v126 = v125 - 1;
        if ( !v126 )
        {
          n184 = 208;
          goto LABEL_160;
        }
        if ( v126 == 1 )
        {
          n184 = 232;
          goto LABEL_160;
        }
        n2_2 = 4294967265LL;
        return sub_1430E92A0(a1, n2_2, v167 - *v7);
      case 6:
        goto LABEL_125;
      case 7:
      case 8:
      case 9:
      case 0xA:
        goto LABEL_178;
      case 0xB:
        n2_11 = sub_1430E4BF0(v9, v14, v6, a1);
        v6 = a6;
        n2 = n2_11;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_11 == 1 )
        {
          *(_DWORD *)a1 = 14;
          n6 = 0x140000000uLL;
        }
        continue;
      case 0xC:
        n2_12 = sub_1430E92F0(a1, 2147483660LL, 0x140000000uLL);
        v6 = a6;
        n2 = n2_12;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_12 == 1 )
        {
          *(_DWORD *)a1 = 14;
          n6 = 0x140000000uLL;
        }
        continue;
      case 0xD:
      case 0xF:
      case 0x10:
        n2_13 = sub_1430E94B0(a1, (_DWORD)v9, (_DWORD)v14, (_DWORD)v6, 0);
        v6 = a6;
        n2 = n2_13;
        v14 = v170;
        n6 = 0x140000000uLL;
        n0x40_1 = 2147483660LL;
        if ( n2_13 != 1 )
          continue;
        sub_1430E9470(a1, 2147483660LL, 0x140000000uLL);
        if ( *(_DWORD *)(a1 + 100) == 1 << ((*(_DWORD *)(a1 + 772) >> 6) & 0x3F) )
          *(_DWORD *)(a1 + 96) = *(_DWORD *)(a1 + 92);
        if ( *(_DWORD *)a1 == 15 )
        {
          v150 = *(_QWORD *)(a1 + 808);
          if ( v150 )
          {
            if ( *(_DWORD *)(v150 + 16) != *(_DWORD *)(v150 + 20) )
            {
              v151 = *(_DWORD *)(a1 + 88);
              v152 = sub_1430E4B10(a1, v151);
              v6 = a6;
              n6 = 0x140000000uLL;
              v14 = v170;
              n0x40_1 = 2147483660LL;
              v153 = v152 + v151;
              v10 = (_BYTE **)a3;
              *(_DWORD *)(a1 + 88) = v153;
              if ( v153 >= *(_DWORD *)(a1 + 100) )
                continue;
            }
          }
          n14 = 14;
          if ( *(_DWORD *)(a1 + 132) )
            n14 = 7;
          *(_DWORD *)a1 = n14;
        }
        else if ( *(_DWORD *)a1 == 16 )
        {
          *(_DWORD *)a1 = 10;
        }
        else if ( *(_DWORD *)(a1 + 4) )
        {
          *(_DWORD *)a1 = 8;
        }
        else
        {
          n14_1 = 14;
          if ( *(_DWORD *)(a1 + 132) )
            n14_1 = 9;
          *(_DWORD *)a1 = n14_1;
        }
        goto LABEL_216;
      case 0xE:
        if ( *(int *)(a1 + 132) >= 0 )
        {
          sub_1430EA0A0(a1, 2147483660LL, 0x140000000uLL);
          if ( (*(_BYTE *)(a1 + 772) & 1) == 0 )
          {
            *(_DWORD *)a1 = 3;
            goto LABEL_216;
          }
          n0x40_4 = *(_QWORD *)(a1 + 16);
          v157 = 0;
          v158 = n0x40_4 & 7;
          if ( (n0x40_4 & 7) != 0 )
          {
            v159 = *(_QWORD *)(a1 + 8);
            n0x40_4 -= v158;
            v157 = v159 & qword_1462B79A0[v158];
            *(_QWORD *)(a1 + 16) = n0x40_4;
            *(_QWORD *)(a1 + 8) = v159 >> v158;
          }
          if ( n0x40_4 < 0x40 )
            *(_QWORD *)(a1 + 8) &= (1LL << n0x40_4) - 1;
          if ( v157 )
          {
            n2 = -15;
            goto LABEL_216;
          }
          if ( !*(_QWORD *)(a1 + 80) )
          {
            v160 = *(_QWORD *)(a1 + 24);
            if ( n0x40_4 >> 3 )
              v160 = *(_QWORD *)(a1 + 24) - (n0x40_4 >> 3);
            n0x40_5 = n0x40_4 - 8 * (n0x40_4 >> 3);
            *(_QWORD *)(a1 + 24) = v160;
            *(_QWORD *)(a1 + 16) = n0x40_5;
            if ( n0x40_5 < 0x40 )
              *(_QWORD *)(a1 + 8) &= (1LL << n0x40_5) - 1;
            *v7 = *(_QWORD *)(a1 + 40) - v160;
            *v10 = *(_BYTE **)(a1 + 24);
          }
          LODWORD(v6) = (_DWORD)a6;
          LODWORD(v14) = (_DWORD)v170;
          *(_DWORD *)a1 = 26;
LABEL_214:
          if ( *(_QWORD *)(a1 + 136) )
          {
            n2 = sub_1430E94B0(a1, (_DWORD)v9, (_DWORD)v14, (_DWORD)v6, 1);
            if ( n2 != 1 )
              goto LABEL_216;
          }
          goto LABEL_220;
        }
        n2 = -10;
        continue;
      case 0x11:
        goto LABEL_84;
      case 0x12:
        goto LABEL_85;
      case 0x13:
        goto LABEL_91;
      case 0x14:
        goto LABEL_93;
      case 0x15:
        goto LABEL_95;
      case 0x16:
        goto LABEL_133;
      case 0x17:
        goto LABEL_142;
      case 0x18:
        goto LABEL_154;
      case 0x19:
        goto LABEL_167;
      case 0x1A:
        goto LABEL_214;
      default:
        continue;
    }
  }
}
