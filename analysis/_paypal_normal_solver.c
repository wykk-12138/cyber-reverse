__int64 __fastcall sub_140D8D2B0(__int64 *a1)
{
  __int64 v1; // rax
  __int64 v2; // rbx
  __int64 v3; // rax
  _UNKNOWN **v4; // rsi
  __int64 v5; // rdi
  __int64 v6; // rsi
  __int64 v7; // rsi
  __int64 v8; // rsi
  __int64 v9; // rsi
  __int64 v10; // rbx
  __int64 v11; // rdi
  __int64 v12; // r8
  __int64 v13; // rsi
  __int64 v14; // rax
  __int64 result; // rax
  __int64 v16; // rax
  __int64 v17; // rcx
  __int64 v18; // rsi
  __int64 v19; // rdi
  _UNKNOWN **v20; // r14
  __int64 v21; // rsi
  __int64 v22; // rdi
  __int64 v23; // r14
  __int64 v24; // r15
  __int64 v25; // r14
  __int64 v26; // rsi
  __int64 v27; // rax
  __int64 v28; // r8
  __int64 v29; // rcx
  __int64 v30; // r8
  __int64 v31; // rax
  __int64 v32; // rcx
  __int64 v33; // rax
  __int64 v34; // rax
  __int64 v35; // rsi
  __int64 v36; // rdi
  __int64 v37; // r14
  __int64 v38; // rax
  __int64 v39; // rax
  __int64 v40; // rax
  __int64 v41; // rax
  __int64 v42; // r14
  __int64 v43; // rax
  __int64 v44; // r14
  __int64 v45; // rax
  __int64 v46; // r14
  __int64 v47; // rax
  __int64 v48; // r14
  __int64 v49; // r15
  __int64 v50; // r14
  __int64 v51; // rax
  __int64 v52; // rax
  __int64 v53; // rax
  __int64 v54; // rcx
  __int64 v55; // rsi
  __int64 v56; // rdi
  __int64 v57; // r14
  __int64 v58; // rax
  __int64 v59; // r14
  __int64 v60; // r15
  __int64 v61; // rax
  __int64 v62; // rax
  __int64 v63; // rax
  __int64 v64; // rsi
  __int64 v65; // rdi
  __int64 v66; // r14
  __int64 v67; // r15
  __int64 v68; // rsi
  __int64 v69; // rax
  __int64 v70; // rcx
  __int64 v71; // rsi
  __int64 v72; // rcx
  _UNKNOWN **v73; // r14
  __int64 v74; // rsi
  __int64 v75; // rdi
  __int64 v76; // r14
  __int64 v77; // r15
  __int64 v78; // rax
  __int64 v79; // r15
  __int64 v80; // r13
  __int64 v81; // rax
  __int64 v82; // r15
  __int64 v83; // rax
  __int64 v84; // rcx
  __int64 v85; // rax
  __int64 v86; // rax
  __int64 v87; // rsi
  __int64 v88; // rdi
  __int64 v89; // r14
  __int64 v90; // r15
  __int64 v91; // rax
  __int64 v92; // r15
  __int64 v93; // r13
  __int64 v94; // r15
  __int64 v95; // rax
  __int64 v96; // rdi
  __int64 v97; // r14
  __int64 v98; // r15
  __int64 v99; // rax
  __int64 v100; // rax
  __int64 v101; // rsi
  __int64 v102; // rcx
  _UNKNOWN **v103; // r14
  __int64 v104; // rdi
  __int64 v105; // r14
  __int64 v106; // r15
  __int64 v107; // rax
  __int64 v108; // rdi
  __int64 v109; // r14
  __int64 v110; // r9
  __int64 v111; // r15
  __int64 v112; // rax
  __int64 v113; // rsi
  __int64 v114; // rdi
  __int64 v115; // rax
  void **v116; // rcx
  __int64 v117; // rdx
  __int64 v118; // rsi
  __int64 v119; // rdi
  __int64 v120; // r14
  __int64 v121; // rdi
  __int64 v122; // rax
  _QWORD *v123; // rbx
  __int64 v124; // [rsp+28h] [rbp-B0h]
  _BYTE v125[24]; // [rsp+30h] [rbp-A8h] BYREF
  __int128 v126; // [rsp+48h] [rbp-90h]
  __int64 v127; // [rsp+58h] [rbp-80h]
  __int128 v128; // [rsp+60h] [rbp-78h] BYREF
  __int128 v129; // [rsp+70h] [rbp-68h]
  __int64 v130; // [rsp+80h] [rbp-58h]
  __int64 v131; // [rsp+88h] [rbp-50h] BYREF
  __int64 v132; // [rsp+90h] [rbp-48h] BYREF
  _QWORD v133[8]; // [rsp+98h] [rbp-40h] BYREF

  *(_OWORD *)v125 = 0;
  v1 = 0x1FFFFFFFFFFFFFF4LL;
  do
  {
    *(_OWORD *)&v133[v1 + 1] = 0;
    *(_OWORD *)&v133[v1 + 3] = 0;
    *(_OWORD *)&v133[v1 + 5] = 0;
    v1 += 6;
  }
  while ( v1 * 8 );
  v2 = *a1;
  switch ( *((_DWORD *)a1 + 14) )
  {
    case 0:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_127;
    case 1:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_122;
    case 2:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_113;
    case 3:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_104;
    case 4:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_98;
    case 5:
      v132 = a1[10];
      a1[10] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_89;
    case 6:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_80;
    case 7:
      v131 = a1[11];
      a1[11] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_70;
    case 8:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_62;
    case 9:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_55;
    case 0xA:
      v132 = a1[10];
      a1[10] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_9;
    case 0xB:
      v133[0] = a1[9];
      a1[9] = 0;
      *((_DWORD *)a1 + 14) = -1;
      goto LABEL_5;
    default:
      sub_143028C10(&unk_144C604C8);
      sub_143028EE0(a1 + 2);
      sub_143028E70(a1[2] + 16, *a1);
      v113 = a1[2];
      v114 = sub_141E54630();
      if ( off_147298AD8[-1] )
        sub_142F900F8();
      v115 = sub_141FFE300(v114, *(_QWORD *)(qword_1472CB278 + 8));
      if ( *(_UNKNOWN **)v115 == &unk_144D88048 || *(_UNKNOWN **)v115 == &unk_144E03640 )
      {
        v117 = sub_141B262B0(v115, &off_146FC1C58);
      }
      else
      {
        v116 = *(void ***)(v115 + 72);
        if ( v116 )
        {
          if ( *v116 == &unk_144D88048 || *v116 == &unk_144E03640 )
            v117 = sub_141B262B0(v116, &off_146FC1C58);
          else
            v117 = sub_141CDA020(v116, &off_146FC1C58);
        }
        else
        {
          v117 = 0;
        }
      }
      sub_143028E70(v113 + 8, v117);
      v118 = *(_QWORD *)(v2 + 16);
      v119 = a1[1];
      v120 = sub_143028C10(&unk_144BDF900);
      sub_143028E70(v120 + 8, v119);
      *(_DWORD *)(v120 + 32) = 0;
      v121 = sub_143028C10(&unk_144FE9240);
      sub_142FABD48(v121, a1[2]);
      v133[0] = sub_1408B61E0(v118, v120, v121);
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)a1 + 14) = 0;
        sub_143028EE0(a1 + 9);
        v122 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
        return sub_142D72040(&off_1449B5258, v133, v122);
      }
LABEL_127:
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v133[0], 0);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_164;
      v84 = a1[2];
      v85 = *(_QWORD *)(v84 + 8);
      if ( !v85 || !*(_DWORD *)(v85 + 8) )
        goto LABEL_53;
      v124 = v84 + 24;
      v86 = sub_141CF62D0(&off_1470983D8, *(_QWORD *)(v84 + 8), &off_146A7F400);
      sub_143028E70(v124, v86);
      v87 = *(_QWORD *)(v2 + 16);
      v88 = sub_143028C10(&unk_144BDF900);
      sub_1408C22E0(v88, &off_1470982F0);
      v89 = sub_143028C10(&unk_144CBDA18);
      *(_QWORD *)(v89 + 104) = &off_146F76688;
      v90 = sub_143028C10(&unk_144D7C578);
      v91 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v91 + 8) = &off_14723C8B8;
      sub_143028E70(v90 + 8, v91);
      sub_143028E70(v89 + 80, v90);
      v92 = *(_QWORD *)(a1[2] + 8);
      v93 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v93 + 40, v92);
      *(_DWORD *)(v93 + 48) = 8;
      sub_141ADAE90(v89, &off_147171D48, v93);
      v94 = sub_143028C10(&unk_144FE9240);
      sub_142FABD60(v94, a1[2]);
      v133[0] = sub_1408B6310(v87, v88, v89, v94);
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)a1 + 14) = 1;
        sub_143028EE0(a1 + 9);
        v95 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
        return sub_142D72040(&off_1449B5258, v133, v95);
      }
LABEL_122:
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v133[0], 0);
      *(_QWORD *)(a1[2] + 32) = &off_146A622F8;
      *(_QWORD *)(a1[2] + 40) = &off_146A622F8;
      v74 = *(_QWORD *)(v2 + 16);
      v75 = sub_143028C10(&unk_144BDF900);
      sub_1408C22E0(v75, &off_147098368);
      v76 = sub_143028C10(&unk_144CBDA18);
      *(_QWORD *)(v76 + 104) = &off_146F76688;
      v77 = sub_143028C10(&unk_144D7C578);
      v78 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v78 + 8) = &off_14723C8B8;
      sub_143028E70(v77 + 8, v78);
      sub_143028E70(v76 + 80, v77);
      v79 = *(_QWORD *)(a1[2] + 8);
      v80 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v80 + 40, v79);
      *(_DWORD *)(v80 + 48) = 8;
      sub_141ADAE90(v76, &off_147171D48, v80);
      v81 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v81 + 40) = &off_14717E4A8;
      *(_DWORD *)(v81 + 48) = 8;
      sub_141ADAE90(v76, &off_146F6D9A8, v81);
      v82 = sub_143028C10(&unk_144FE9240);
      sub_142FABD6C(v82, a1[2]);
      v133[0] = sub_1408B6310(v74, v75, v76, v82);
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)a1 + 14) = 2;
        sub_143028EE0(a1 + 9);
        v83 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
        return sub_142D72040(&off_1449B5258, v133, v83);
      }
LABEL_113:
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v133[0], 0);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_164;
      v70 = *(_QWORD *)(a1[2] + 32);
      if ( v70 && *(_DWORD *)(v70 + 8) )
      {
        sub_143028C10(&unk_144C606B0);
        sub_143028EE0(a1 + 3);
        sub_143028E70(a1[3] + 16, a1[2]);
        *(_QWORD *)(a1[3] + 8) = &off_146A622F8;
        v71 = *(_QWORD *)(v2 + 16);
        v72 = *(_QWORD *)(*(_QWORD *)(a1[3] + 16) + 40LL);
        if ( v72 && *(_DWORD *)(v72 + 8) )
          v73 = *(_UNKNOWN ***)(*(_QWORD *)(a1[3] + 16) + 40LL);
        else
          v73 = &off_1470985E8;
        v96 = sub_143028C10(&unk_144BDF900);
        sub_1408C22E0(v96, v73);
        v97 = sub_143028C10(&unk_144CB7DE8);
        sub_14130C960(v97);
        sub_14130CC50(v97, &off_146DD3A08, *(_QWORD *)(*(_QWORD *)(a1[3] + 16) + 32LL));
        v98 = sub_143028C10(&unk_144FE9240);
        sub_142FABDA8(v98, a1[3]);
        v133[0] = sub_1408B6310(v71, v96, v97, v98);
        if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
        {
          *((_DWORD *)a1 + 14) = 3;
          sub_143028EE0(a1 + 9);
          v99 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
          return sub_142D72040(&off_1449B5258, v133, v99);
        }
LABEL_104:
        if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v133[0], 0);
        v54 = *(_QWORD *)(a1[3] + 8);
        if ( v54 && *(_DWORD *)(v54 + 8) )
        {
          v55 = sub_143028C10(&unk_144D7C1E0);
          if ( off_147298AD8[-1] )
            sub_142F900F8();
          v56 = *(_QWORD *)(qword_1472CB278 + 8);
          v57 = sub_143028C10(&unk_144D7C578);
          v58 = sub_143028C10(&unk_145496718);
          *(_QWORD *)(v58 + 8) = &off_14723C8B8;
          sub_143028E70(v57 + 8, v58);
          sub_143028E70(v55 + 80, v57);
          v59 = *(_QWORD *)(a1[3] + 8);
          v60 = sub_143028C10(&unk_144D7CCC0);
          sub_143028E70(v60 + 40, v59);
          *(_DWORD *)(v60 + 48) = 8;
          sub_141ADAE90(v55, &off_14716D5F8, v60);
          v61 = sub_141ADD070(v55, 0);
          v62 = sub_141E166A0(v56, v61);
          v63 = sub_141D09B60(v62);
          *(_DWORD *)v125 = 61;
          v64 = sub_141CFA600(v63, v125, 1, 2);
          v65 = *(_QWORD *)(v2 + 16);
          v66 = sub_143028C10(&unk_144BDF900);
          sub_1408C22E0(v66, &off_147098740);
          v67 = sub_143028C10(&unk_144CB7DE8);
          sub_14130C960(v67);
          sub_14130CC50(v67, &off_14716D3D0, v64);
          v68 = sub_143028C10(&unk_144FE9240);
          sub_142FABD84(v68, *(_QWORD *)(a1[3] + 16));
          v133[0] = sub_1408B6310(v65, v66, v67, v68);
          if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
          {
            *((_DWORD *)a1 + 14) = 4;
            sub_143028EE0(a1 + 9);
            v69 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
            return sub_142D72040(&off_1449B5258, v133, v69);
          }
LABEL_98:
          if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
            sub_141DC8280(v133[0], 0);
        }
        a1[3] = 0;
      }
      *(_QWORD *)(a1[2] + 56) = &off_146A622F8;
      *(_QWORD *)(a1[2] + 64) = &off_146A622F8;
      *(_QWORD *)(a1[2] + 72) = &off_146A622F8;
      *(_QWORD *)(a1[2] + 80) = &off_146A622F8;
      *(_QWORD *)(a1[2] + 88) = &off_146A622F8;
      v35 = sub_143028C10(&unk_144D7C1E0);
      v36 = a1[2];
      v37 = sub_143028C10(&unk_144D7C578);
      v38 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v38 + 8) = &off_14723C8B8;
      sub_143028E70(v37 + 8, v38);
      sub_143028E70(v35 + 80, v37);
      v39 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v39 + 40) = &off_146F5FF08;
      *(_DWORD *)(v39 + 48) = 8;
      sub_141ADAE90(v35, &off_147184E58, v39);
      v40 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v40 + 40) = &off_14727D118;
      *(_DWORD *)(v40 + 48) = 9;
      sub_141ADAE90(v35, &off_1470ACAF8, v40);
      v41 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v41 + 40) = &off_14701B338;
      *(_DWORD *)(v41 + 48) = 8;
      sub_141ADAE90(v35, &off_1470B0BD8, v41);
      v42 = sub_143028C10(&unk_144D7CCC0);
      v43 = sub_141AAF6B0(24);
      sub_143028E70(v42 + 40, v43);
      *(_DWORD *)(v42 + 48) = 6;
      sub_141ADAE90(v35, &off_146FD3A30, v42);
      v44 = sub_143028C10(&unk_144D7CCC0);
      v45 = sub_141AAF6B0(1080);
      sub_143028E70(v44 + 40, v45);
      *(_DWORD *)(v44 + 48) = 6;
      sub_141ADAE90(v35, &off_1471530D0, v44);
      v46 = sub_143028C10(&unk_144D7CCC0);
      v47 = sub_141AAF6B0(1920);
      sub_143028E70(v46 + 40, v47);
      *(_DWORD *)(v46 + 48) = 6;
      sub_141ADAE90(v35, &off_147153188, v46);
      v48 = *(_QWORD *)(*(_QWORD *)(*(_QWORD *)(v2 + 16) + 8LL) + 8LL);
      v49 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v49 + 40, v48);
      *(_DWORD *)(v49 + 48) = 8;
      sub_141ADAE90(v35, &off_1471796E8, v49);
      v50 = sub_143028C10(&unk_144D7CCC0);
      v51 = sub_141AAF6B0(-120);
      sub_143028E70(v50 + 40, v51);
      *(_DWORD *)(v50 + 48) = 6;
      sub_141ADAE90(v35, &off_14716E280, v50);
      v52 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v52 + 40) = &off_146B68618;
      *(_DWORD *)(v52 + 48) = 8;
      sub_141ADAE90(v35, &off_147003B30, v52);
      sub_143028E70(v36 + 48, v35);
      *(_QWORD *)(a1[2] + 96) = &off_146A622F8;
      v132 = sub_140D8BA90(a1[2], &off_1470B9658, 1);
      if ( (*(_DWORD *)(v132 + 52) & 0x1600000) == 0 )
      {
        *((_DWORD *)a1 + 14) = 5;
        sub_143028EE0(a1 + 10);
        v53 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
        return sub_142D72040(&unk_144988988, &v132, v53);
      }
LABEL_89:
      if ( (*(_DWORD *)(v132 + 52) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v132, 0);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_164;
      if ( !(unsigned int)sub_141CF4290(*(_QWORD *)(a1[2] + 80), &off_146B67428) )
        goto LABEL_12;
      v32 = *(_QWORD *)(a1[2] + 88);
      if ( !v32 || !*(_DWORD *)(v32 + 8) )
        goto LABEL_12;
      sub_143028C10(&unk_144C60788);
      sub_143028EE0(a1 + 4);
      sub_143028E70(a1[4] + 24, a1[2]);
      v33 = sub_1410E43F0(*(_QWORD *)(*(_QWORD *)(a1[4] + 24) + 88LL));
      if ( v33 && (v100 = sub_141ADAE30(v33, &off_14710E630)) != 0 )
        v34 = (*(__int64 (__fastcall **)(__int64, _UNKNOWN **))(*(_QWORD *)v100 + 80LL))(v100, &off_146FC54D8);
      else
        v34 = 0;
      sub_141ADF490(v34);
      sub_143028EE0(a1 + 6);
      *(_QWORD *)(a1[4] + 8) = &off_146A622F8;
      *(_QWORD *)(a1[4] + 16) = 0;
      v101 = *(_QWORD *)(v2 + 16);
      v102 = *(_QWORD *)(*(_QWORD *)(a1[4] + 24) + 96LL);
      if ( v102 && *(_DWORD *)(v102 + 8) )
        v103 = *(_UNKNOWN ***)(*(_QWORD *)(a1[4] + 24) + 96LL);
      else
        v103 = &off_147098540;
      v104 = sub_143028C10(&unk_144BDF900);
      sub_1408C22E0(v104, v103);
      v105 = sub_143028C10(&unk_144CB7DE8);
      sub_14130C960(v105);
      sub_14130CC50(v105, &off_146DD3A08, *(_QWORD *)(*(_QWORD *)(a1[4] + 24) + 88LL));
      v106 = sub_143028C10(&unk_144FE9240);
      sub_142FABDC0(v106, a1[4]);
      v133[0] = sub_1408B6310(v101, v104, v105, v106);
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)a1 + 14) = 6;
        sub_143028EE0(a1 + 9);
        v107 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
        return sub_142D72040(&off_1449B5258, v133, v107);
      }
LABEL_80:
      if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v133[0], 0);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_11;
      v28 = a1[4];
      v29 = *(_QWORD *)(v28 + 8);
      if ( !v29 )
        goto LABEL_11;
      if ( !*(_DWORD *)(v29 + 8) )
        goto LABEL_11;
      v30 = *(_QWORD *)(v28 + 16);
      if ( !v30 )
        goto LABEL_11;
      v131 = sub_1408A2FA0(*(_QWORD *)(v2 + 8), v29, v30, 0);
      if ( (*(_DWORD *)(v131 + 52) & 0x1600000) == 0 )
      {
        *((_DWORD *)a1 + 14) = 7;
        sub_143028EE0(a1 + 11);
        v31 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
        return sub_142D72040(&off_1449C6C48, &v131, v31);
      }
LABEL_70:
      if ( (*(_DWORD *)(v131 + 52) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v131, 0);
      v21 = *(_QWORD *)(v131 + 56);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_164;
      if ( v21 && *(_QWORD *)(v21 + 16) )
      {
        sub_143028C10(&unk_144C60860);
        sub_143028EE0(a1 + 5);
        *(_QWORD *)(a1[5] + 8) = &off_146A622F8;
        *(_QWORD *)(a1[5] + 16) = 0;
        v22 = *(_QWORD *)(v2 + 16);
        v23 = *(_QWORD *)(v21 + 8);
        if ( !v23 )
        {
          v23 = sub_143028C10(&unk_144DDB770);
          sub_141E532B0(v23, a1[6]);
        }
        v24 = sub_143028C10(&unk_144BDF900);
        sub_143028E70(v24 + 8, v23);
        *(_DWORD *)(v24 + 32) = 0;
        v25 = sub_143028C10(&unk_144FE9240);
        v26 = *(_QWORD *)(v21 + 16);
        sub_142FABDD8(v25, a1[5]);
        v133[0] = sub_1408B6310(v22, v24, v26, v25);
        if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
        {
          *((_DWORD *)a1 + 14) = 8;
          sub_143028EE0(a1 + 9);
          v27 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
          return sub_142D72040(&off_1449B5258, v133, v27);
        }
LABEL_62:
        if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v133[0], 0);
        if ( (unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        {
          v17 = a1[5];
          if ( *(_QWORD *)(v17 + 16) )
          {
            v18 = *(_QWORD *)(v2 + 16);
            v19 = *(_QWORD *)(v17 + 8);
            if ( v19 && *(_DWORD *)(v19 + 8) )
              v20 = (_UNKNOWN **)v19;
            else
              v20 = &off_147098258;
            v108 = sub_143028C10(&unk_144BDF900);
            sub_1408C22E0(v108, v20);
            v109 = *(_QWORD *)(a1[5] + 16);
            v110 = *(_QWORD *)(qword_1472C6B00 + 88);
            if ( !v110 )
            {
              v111 = sub_143028C10(&unk_144FE9240);
              sub_142FABD18(v111, &off_147285A70);
              sub_143028E70(qword_1472C6B00 + 88, v111);
              v110 = v111;
            }
            v133[0] = sub_1408B6310(v18, v108, v109, v110);
            if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
            {
              *((_DWORD *)a1 + 14) = 9;
              sub_143028EE0(a1 + 9);
              v112 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
              return sub_142D72040(&off_1449B5258, v133, v112);
            }
LABEL_55:
            if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
              sub_141DC8280(v133[0], 0);
          }
        }
        a1[5] = 0;
      }
      if ( (unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
      {
        v132 = sub_140D8BA90(*(_QWORD *)(a1[4] + 24), &off_146F7C1E0, 0);
        if ( (*(_DWORD *)(v132 + 52) & 0x1600000) == 0 )
        {
          *((_DWORD *)a1 + 14) = 10;
          sub_143028EE0(a1 + 10);
          v16 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
          return sub_142D72040(&unk_144988988, &v132, v16);
        }
LABEL_9:
        if ( (*(_DWORD *)(v132 + 52) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v132, 0);
      }
LABEL_11:
      a1[4] = 0;
      a1[6] = 0;
LABEL_12:
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) || !*(_BYTE *)(v2 + 24) )
        goto LABEL_164;
      v3 = *(_QWORD *)(a1[2] + 56);
      if ( v3 && *(_DWORD *)(v3 + 8) )
      {
        v4 = &off_146A7ABA8;
        if ( !(unsigned int)sub_141CFA770(*(_QWORD *)(a1[2] + 56), 63) )
          v4 = &off_146B27640;
        sub_141DC76E0(&v125[8], 68, 4);
        v128 = *(_OWORD *)&v125[8];
        v129 = v126;
        v130 = v127;
        v5 = *(_QWORD *)(a1[2] + 56);
        if ( BYTE4(v126) || !v5 )
          goto LABEL_22;
        if ( (unsigned int)v129 > (unsigned int)v130 )
          goto LABEL_163;
        if ( *(_DWORD *)(v5 + 8) <= (unsigned int)(v130 - v129) )
        {
          sub_141D2B8E0(*((_QWORD *)&v129 + 1) + 2LL * (unsigned int)v129, v5 + 12, 2LL * *(unsigned int *)(v5 + 8));
          LODWORD(v129) = *(_DWORD *)(v5 + 8) + v129;
        }
        else
        {
LABEL_22:
          sub_141DC79E0(&v128, *(_QWORD *)(a1[2] + 56));
        }
        if ( BYTE4(v129) )
          goto LABEL_27;
        if ( (unsigned int)v129 > (unsigned int)v130 )
          goto LABEL_163;
        if ( *((_DWORD *)v4 + 2) > (unsigned int)(v130 - v129) )
        {
LABEL_27:
          sub_141DC79E0(&v128, v4);
        }
        else
        {
          sub_141D2B8E0(
            *((_QWORD *)&v129 + 1) + 2LL * (unsigned int)v129,
            (char *)v4 + 12,
            2LL * *((unsigned int *)v4 + 2));
          LODWORD(v129) = *((_DWORD *)v4 + 2) + v129;
        }
        if ( (unsigned int)v129 <= (unsigned int)v130 )
        {
          if ( (unsigned int)(v130 - v129) >= 0x2F )
          {
            sub_141D2B8E0(*((_QWORD *)&v129 + 1) + 2LL * (unsigned int)v129, &unk_147163134, 94);
            LODWORD(v129) = v129 + 47;
          }
          else
          {
            sub_141DC7B80(&v128, &off_147163128);
          }
          v6 = *(_QWORD *)(a1[2] + 64);
          if ( BYTE4(v129) || !v6 )
            goto LABEL_37;
          if ( (unsigned int)v129 > (unsigned int)v130 )
            goto LABEL_163;
          if ( *(_DWORD *)(v6 + 8) <= (unsigned int)(v130 - v129) )
          {
            sub_141D2B8E0(*((_QWORD *)&v129 + 1) + 2LL * (unsigned int)v129, v6 + 12, 2LL * *(unsigned int *)(v6 + 8));
            LODWORD(v129) = *(_DWORD *)(v6 + 8) + v129;
          }
          else
          {
LABEL_37:
            sub_141DC79E0(&v128, *(_QWORD *)(a1[2] + 64));
          }
          if ( (unsigned int)v129 <= (unsigned int)v130 )
          {
            v7 = *((_QWORD *)&v129 + 1) + 2LL * (unsigned int)v129;
            if ( (unsigned int)(v130 - v129) >= 0x15 )
            {
              *(_OWORD *)v7 = xmmword_145E98B20;
              *(_OWORD *)(v7 + 16) = xmmword_145E98B30;
              *(_QWORD *)(v7 + 32) = 0x77006F006C0066LL;
              *(_WORD *)(v7 + 40) = 61;
              LODWORD(v129) = v129 + 21;
            }
            else
            {
              sub_141DC7B80(&v128, &off_146A7B2B0);
            }
            v8 = *(_QWORD *)(a1[2] + 72);
            if ( BYTE4(v129) || !v8 )
              goto LABEL_47;
            if ( (unsigned int)v129 <= (unsigned int)v130 )
            {
              if ( *(_DWORD *)(v8 + 8) <= (unsigned int)(v130 - v129) )
              {
                sub_141D2B8E0(
                  *((_QWORD *)&v129 + 1) + 2LL * (unsigned int)v129,
                  v8 + 12,
                  2LL * *(unsigned int *)(v8 + 8));
                LODWORD(v129) = *(_DWORD *)(v8 + 8) + v129;
                goto LABEL_49;
              }
LABEL_47:
              sub_141DC79E0(&v128, *(_QWORD *)(a1[2] + 72));
LABEL_49:
              v9 = sub_141DC7870(&v128);
              v10 = *(_QWORD *)(v2 + 16);
              v11 = sub_143028C10(&unk_144BDF900);
              sub_1408C22E0(v11, v9);
              v12 = *(_QWORD *)(qword_1472C6B00 + 104);
              if ( !v12 )
              {
                v13 = sub_143028C10(&unk_144FE9240);
                sub_142FABD30(v13, &off_147285A70);
                sub_143028E70(qword_1472C6B00 + 104, v13);
                v12 = v13;
              }
              v133[0] = sub_1408B61E0(v10, v11, v12);
              if ( (*(_DWORD *)(v133[0] + 52LL) & 0x1600000) == 0 )
              {
                *((_DWORD *)a1 + 14) = 11;
                sub_143028EE0(a1 + 9);
                v14 = sub_142BF2060(&off_144918C20, a1, a1 + 8);
                return sub_142D72040(&off_1449B5258, v133, v14);
              }
LABEL_5:
              if ( (*(_DWORD *)(v133[0] + 52LL) & 0x11000000) != 0x1000000 )
                sub_141DC8280(v133[0], 0);
              goto LABEL_164;
            }
          }
        }
LABEL_163:
        sub_141D2D430();
        __debugbreak();
      }
LABEL_53:
      sub_140F9EFA0(*(_QWORD *)(v2 + 8), &off_146E3B5F0, &off_146A76FD0);
LABEL_164:
      *((_DWORD *)a1 + 14) = -2;
      a1[2] = 0;
      v123 = a1 + 8;
      if ( a1[8] )
      {
        result = sub_14288E930(*v123, 0);
        if ( !(_DWORD)result )
        {
          __ExceptionPtrRethrow((const void *)0x18);
          __debugbreak();
        }
      }
      else
      {
        if ( *(&off_1472AA1B0 - 1) )
          sub_142F91CBA();
        return sub_143028EE0(v123);
      }
      return result;
  }
}
