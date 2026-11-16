double __fastcall sub_140F74A40(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v8; // r14
  __int64 v9; // rdi
  __int64 v10; // rax
  __int64 v11; // r15
  __int64 v12; // r15
  __int64 v13; // r15
  unsigned int v14; // r13d
  __int64 v15; // rdi
  __int64 v16; // rax
  __int64 v17; // r15
  __int64 v18; // r15
  __int64 v19; // r15
  unsigned int v20; // r13d
  __int64 v21; // rdi
  __int64 v22; // rax
  __int64 v23; // r15
  __int64 v24; // r15
  __int64 v25; // r15
  unsigned int v26; // r13d
  __int64 v27; // rdi
  __int64 v28; // rax
  __int64 v29; // r15
  __int64 v30; // r15
  __int64 v31; // r15
  unsigned int v32; // r13d
  __int64 v33; // rdi
  __int64 v34; // rax
  __int64 v35; // r15
  __int64 v36; // r15
  __int64 v37; // r15
  unsigned int v38; // r13d
  __int64 v39; // rdi
  __int64 v40; // rbp
  __int64 v41; // rax
  __int64 v42; // rax
  __int64 v43; // rbp
  __int64 v44; // rbp
  __int64 v45; // rbp
  unsigned int v46; // r15d
  __int64 v47; // rdi
  __int64 v48; // rax
  __int64 v49; // rbp
  __int64 v50; // rbp
  __int64 v51; // rdx
  __int64 v52; // rbp
  __int64 v53; // rdx
  __int64 v54; // rbp
  __int64 v55; // rbp
  unsigned int v56; // r15d
  __int64 v57; // rdi
  __int64 v58; // rax
  int v59; // ecx
  __int64 v60; // rbp
  __int64 v61; // rbp
  __int64 v62; // rbp
  __int64 v63; // rbp
  unsigned int v64; // r15d
  __int64 v65; // rdi
  __int64 v66; // rax
  __int64 v67; // rsi
  __int64 v68; // rsi
  __int64 v69; // rsi
  double result; // xmm0_8
  __int64 v71; // rsi
  unsigned int v72; // ebp

  v8 = sub_143028C10(&unk_144C93B60);
  sub_143028E70(v8 + 8, a3);
  v9 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v9 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v9 + 48) = &off_147236DD0;
  v10 = sub_141CF6230(a2, &off_146A66D50);
  sub_143028E70(v9 + 8, v10);
  v11 = sub_143028C10(&unk_145181938);
  sub_142FB1F34(v11, v8);
  sub_143028E70(v9 + 16, v11);
  v12 = sub_143028C10(&unk_1451818C0);
  sub_142FB1F40(v12, v8);
  sub_143028E70(v9 + 24, v12);
  ++*(_DWORD *)(a1 + 20);
  v13 = *(_QWORD *)(a1 + 8);
  v14 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v13 + 8) > v14 )
  {
    *(_DWORD *)(a1 + 16) = v14 + 1;
    sub_143028E70(v13 + 8LL * v14 + 16, v9);
  }
  else
  {
    sub_142895DB0(a1, v9);
  }
  v15 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v15 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v15 + 48) = &off_147236DD0;
  v16 = sub_141CF6230(a2, &off_146A66F70);
  sub_143028E70(v15 + 8, v16);
  v17 = sub_143028C10(&unk_145181938);
  sub_142FB1F4C(v17, v8);
  sub_143028E70(v15 + 16, v17);
  v18 = sub_143028C10(&unk_1451818C0);
  sub_142FB1F58(v18, v8);
  sub_143028E70(v15 + 24, v18);
  ++*(_DWORD *)(a1 + 20);
  v19 = *(_QWORD *)(a1 + 8);
  v20 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v19 + 8) > v20 )
  {
    *(_DWORD *)(a1 + 16) = v20 + 1;
    sub_143028E70(v19 + 8LL * v20 + 16, v15);
  }
  else
  {
    sub_142895DB0(a1, v15);
  }
  v21 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v21 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v21 + 48) = &off_147236DD0;
  v22 = sub_141CF6230(a2, &off_146A668C8);
  sub_143028E70(v21 + 8, v22);
  *(_QWORD *)(v21 + 64) = 0x4069000000000000LL;
  v23 = sub_143028C10(&unk_145181938);
  sub_142FB1F64(v23, v8);
  sub_143028E70(v21 + 16, v23);
  v24 = sub_143028C10(&unk_1451818C0);
  sub_142FB1F70(v24, v8);
  sub_143028E70(v21 + 24, v24);
  ++*(_DWORD *)(a1 + 20);
  v25 = *(_QWORD *)(a1 + 8);
  v26 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v25 + 8) > v26 )
  {
    *(_DWORD *)(a1 + 16) = v26 + 1;
    sub_143028E70(v25 + 8LL * v26 + 16, v21);
  }
  else
  {
    sub_142895DB0(a1, v21);
  }
  v27 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v27 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v27 + 48) = &off_147236DD0;
  v28 = sub_141CF6230(a2, &off_146A668F8);
  sub_143028E70(v27 + 8, v28);
  v29 = sub_143028C10(&unk_145181938);
  sub_142FB1F7C(v29, v8);
  sub_143028E70(v27 + 16, v29);
  v30 = sub_143028C10(&unk_1451818C0);
  sub_142FB1F88(v30, v8);
  sub_143028E70(v27 + 24, v30);
  ++*(_DWORD *)(a1 + 20);
  v31 = *(_QWORD *)(a1 + 8);
  v32 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v31 + 8) > v32 )
  {
    *(_DWORD *)(a1 + 16) = v32 + 1;
    sub_143028E70(v31 + 8LL * v32 + 16, v27);
  }
  else
  {
    sub_142895DB0(a1, v27);
  }
  v33 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v33 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v33 + 48) = &off_147236DD0;
  v34 = sub_141CF6230(a2, &off_146A66B08);
  sub_143028E70(v33 + 8, v34);
  v35 = sub_143028C10(&unk_145181938);
  sub_142FB1F94(v35, v8);
  sub_143028E70(v33 + 16, v35);
  v36 = sub_143028C10(&unk_1451818C0);
  sub_142FB1FA0(v36, v8);
  sub_143028E70(v33 + 24, v36);
  ++*(_DWORD *)(a1 + 20);
  v37 = *(_QWORD *)(a1 + 8);
  v38 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v37 + 8) > v38 )
  {
    *(_DWORD *)(a1 + 16) = v38 + 1;
    sub_143028E70(v37 + 8LL * v38 + 16, v33);
  }
  else
  {
    sub_142895DB0(a1, v33);
  }
  v39 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v39 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v39 + 48) = &off_147236DD0;
  sub_143028E70(v39 + 8, a4);
  *(_QWORD *)(v39 + 64) = 0x4059000000000000LL;
  v40 = sub_143028DA0(&unk_145DDB978, 2);
  v41 = sub_141CF6230(a2, &off_146A67CF0);
  sub_143028E70(v40 + 16, v41);
  v42 = sub_141CF6230(a2, &off_146A67310);
  sub_143028E70(v40 + 24, v42);
  sub_143028E70(v39 + 48, v40);
  v43 = sub_143028C10(&unk_145181938);
  sub_142FB1FAC(v43, v8);
  sub_143028E70(v39 + 16, v43);
  v44 = sub_143028C10(&unk_1451818C0);
  sub_142FB1FB8(v44, v8);
  sub_143028E70(v39 + 24, v44);
  ++*(_DWORD *)(a1 + 20);
  v45 = *(_QWORD *)(a1 + 8);
  v46 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v45 + 8) > v46 )
  {
    *(_DWORD *)(a1 + 16) = v46 + 1;
    sub_143028E70(v45 + 8LL * v46 + 16, v39);
  }
  else
  {
    sub_142895DB0(a1, v39);
  }
  *(_DWORD *)(v8 + 16) = *(_DWORD *)(a1 + 16);
  v47 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v47 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v47 + 48) = &off_147236DD0;
  v48 = sub_141CF6230(a2, &off_146A66BC0);
  sub_143028E70(v47 + 8, v48);
  *(_QWORD *)(v47 + 64) = 0x4062C00000000000LL;
  *(_BYTE *)(v47 + 72) = 1;
  v49 = sub_143028C10(&unk_145181938);
  sub_142FB1FC4(v49, v8);
  sub_143028E70(v47 + 16, v49);
  v50 = sub_143028C10(&unk_1451818C0);
  sub_142FB1FD0(v50, v8);
  sub_143028E70(v47 + 24, v50);
  v51 = *(_QWORD *)(qword_1472C6F90 + 232);
  if ( !v51 )
  {
    v52 = sub_143028C10(&unk_145576070);
    sub_142FB1EBC(v52, &off_147285230);
    sub_143028E70(qword_1472C6F90 + 232, v52);
    v51 = v52;
  }
  sub_143028E70(v47 + 40, v51);
  v53 = *(_QWORD *)(qword_1472C6F90 + 240);
  if ( !v53 )
  {
    v54 = sub_143028C10(&unk_145594358);
    sub_142FB1EC8(v54, (__int64)&off_147285230);
    sub_143028E70(qword_1472C6F90 + 240, v54);
    v53 = v54;
  }
  sub_143028E70(v47 + 32, v53);
  ++*(_DWORD *)(a1 + 20);
  v55 = *(_QWORD *)(a1 + 8);
  v56 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v55 + 8) > v56 )
  {
    *(_DWORD *)(a1 + 16) = v56 + 1;
    sub_143028E70(v55 + 8LL * v56 + 16, v47);
  }
  else
  {
    sub_142895DB0(a1, v47);
  }
  v57 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v57 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v57 + 48) = &off_147236DD0;
  v58 = sub_141CF6230(a2, &off_146A67578);
  sub_143028E70(v57 + 8, v58);
  *(_QWORD *)(v57 + 64) = 0x4061800000000000LL;
  v59 = *(_DWORD *)(v8 + 16);
  *(_BYTE *)(v57 + 76) = 1;
  *(_DWORD *)(v57 + 80) = v59;
  v60 = sub_143028C10(&unk_145181938);
  sub_142FB1FDC(v60, v8);
  sub_143028E70(v57 + 16, v60);
  v61 = sub_143028C10(&unk_1451818C0);
  sub_142FB1FE8(v61, v8);
  sub_143028E70(v57 + 24, v61);
  v62 = sub_143028C10(&unk_145594358);
  sub_142FB1FF4(v62, v8);
  sub_143028E70(v57 + 32, v62);
  ++*(_DWORD *)(a1 + 20);
  v63 = *(_QWORD *)(a1 + 8);
  v64 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v63 + 8) > v64 )
  {
    *(_DWORD *)(a1 + 16) = v64 + 1;
    sub_143028E70(v63 + 8LL * v64 + 16, v57);
  }
  else
  {
    sub_142895DB0(a1, v57);
  }
  v65 = sub_143028C10(&unk_144C93A00);
  *(_QWORD *)(v65 + 64) = 0x4060400000000000LL;
  *(_QWORD *)(v65 + 48) = &off_147236DD0;
  v66 = sub_141CF6230(a2, &off_146A66A70);
  sub_143028E70(v65 + 8, v66);
  *(_QWORD *)(v65 + 64) = 0x4061800000000000LL;
  v67 = sub_143028C10(&unk_145181938);
  sub_142FB2000(v67, v8);
  sub_143028E70(v65 + 16, v67);
  v68 = sub_143028C10(&unk_1451818C0);
  sub_142FB200C(v68, v8);
  sub_143028E70(v65 + 24, v68);
  v69 = sub_143028C10(&unk_145997480);
  sub_142FB2018(v69, v8);
  result = sub_143028E70(v65 + 56, v69);
  ++*(_DWORD *)(a1 + 20);
  v71 = *(_QWORD *)(a1 + 8);
  v72 = *(_DWORD *)(a1 + 16);
  if ( *(_DWORD *)(v71 + 8) > v72 )
  {
    *(_DWORD *)(a1 + 16) = v72 + 1;
    return sub_143028E70(v71 + 8LL * v72 + 16, v65);
  }
  else
  {
    sub_142895DB0(a1, v65);
  }
  return result;
}
