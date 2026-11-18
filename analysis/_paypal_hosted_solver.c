__int64 __fastcall sub_141113680(__int64 *a1)
{
  __int64 v1; // rax
  __int64 v2; // rbx
  __int64 v3; // rdi
  _UNKNOWN **v4; // rdx
  _QWORD *v5; // rsi
  __int64 v6; // rcx
  __int64 v7; // rdi
  __int64 *v8; // rsi
  __int64 v9; // rdi
  __int64 v10; // r14
  __int64 v11; // rax
  __int64 v12; // rax
  __int64 v13; // r14
  __int64 v14; // r15
  __int64 v15; // rax
  __int64 v16; // r15
  __int64 v17; // r13
  __int64 v18; // r15
  __int64 v19; // r13
  __int64 v20; // r15
  __int64 v21; // r13
  __int64 v22; // rax
  __int64 v23; // rax
  __int64 v24; // rax
  __int64 v25; // rax
  __int64 v26; // r13
  __int64 v27; // r12
  __int64 v28; // rcx
  __int64 v29; // rdi
  _UNKNOWN **v30; // r14
  __int64 v31; // r15
  __int64 v32; // r14
  __int64 v33; // r13
  __int64 v34; // rax
  __int64 result; // rax
  __int64 v36; // rdi
  __int64 v37; // rcx
  _UNKNOWN **v38; // rdx
  __int64 v39; // rdx
  __int64 v40; // rcx
  __int64 v41; // rcx
  __int64 v42; // rcx
  __int64 v43; // rax
  __int64 v44; // rcx
  __int64 v45; // rdi
  _QWORD *v46; // rsi
  __int64 v47; // rdi
  __int64 v48; // r14
  __int64 v49; // rax
  __int64 v50; // rax
  __int64 v51; // r14
  __int64 v52; // r15
  __int64 v53; // rax
  __int64 v54; // r15
  __int64 v55; // r13
  __int64 v56; // r15
  __int64 v57; // r13
  __int64 v58; // rax
  __int64 v59; // rax
  __int64 v60; // rax
  __int64 v61; // r15
  __int64 v62; // r13
  __int64 v63; // rax
  __int64 v64; // rax
  __int64 v65; // rax
  __int64 v66; // rax
  __int64 v67; // r13
  __int64 v68; // rax
  __int64 v69; // r13
  __int64 v70; // rax
  __int64 v71; // r13
  __int64 v72; // rax
  __int64 v73; // r13
  __int64 v74; // r12
  __int64 v75; // rax
  __m128d v76; // xmm0
  int n0x7FFFFFFF; // ecx
  int n0x7FFFFFFF_1; // eax
  int n0x7FFFFFFF_2; // r13d
  __int64 v80; // r12
  __int64 v81; // rax
  __int64 v82; // r15
  __int64 v83; // r13
  __int64 v84; // r12
  __int64 v85; // rax
  __int64 v86; // r15
  __int64 v87; // r13
  __int64 v88; // rax
  __int64 v89; // rax
  __int64 v90; // rax
  __int64 v91; // r13
  __int64 v92; // r12
  __int64 v93; // rcx
  __int64 v94; // rdi
  __int64 v95; // r14
  __int64 v96; // r15
  __int64 v97; // rax
  __int64 v98; // r15
  __int64 v99; // r13
  __int64 v100; // rax
  __int64 v101; // rax
  __int64 v102; // rax
  __int64 v103; // rdi
  __int64 v104; // r14
  __int64 v105; // r15
  __int64 v106; // r13
  __int64 v107; // rdi
  __int64 v108; // rax
  __int64 v109; // rcx
  __int64 v110; // rdi
  __int64 v111; // rax
  int v112; // eax
  __int64 v113; // rcx
  __int64 v114; // r14
  __int64 v115; // rax
  int v116; // eax
  __int64 v117; // rcx
  __int64 v118; // rax
  __int64 v119; // rax
  int v120; // eax
  __int64 v121; // rcx
  __int64 v122; // rax
  _UNKNOWN **v123; // rdx
  _UNKNOWN **v124; // rdx
  __int64 v125; // rdi
  __int64 v126; // rax
  __int64 v127; // rdi
  __int64 v128; // r14
  __int64 v129; // rax
  __int64 v130; // r14
  __int64 v131; // r15
  __int64 v132; // r14
  __int64 v133; // r15
  __int64 v134; // rax
  __int64 v135; // rcx
  __int64 v136; // r14
  int v137; // r13d
  __int64 v138; // rax
  __int64 v139; // rax
  __int64 v140; // r14
  __int64 v141; // r13
  __int64 v142; // rdi
  __int64 v143; // r14
  __int64 v144; // rax
  __int64 v145; // rax
  __int64 v146; // r14
  __int64 v147; // r15
  __int64 v148; // rax
  __int64 v149; // rax
  int v150; // eax
  __int64 v151; // rcx
  __int64 v152; // rax
  __int64 v153; // r15
  __int64 v154; // rax
  __int64 v155; // r13
  __int64 v156; // r15
  __int64 v157; // rax
  int v158; // eax
  __int64 v159; // rcx
  __int64 v160; // rax
  __int64 v161; // r15
  __int64 v162; // rax
  __int64 v163; // r13
  __int64 v164; // r15
  __int64 v165; // rax
  __int64 v166; // r15
  __int64 v167; // rax
  __int64 v168; // r13
  __int64 v169; // r15
  __int64 v170; // rax
  __int64 v171; // r15
  __int64 v172; // rax
  __int64 v173; // r13
  __int64 v174; // r15
  __int64 v175; // rax
  __int64 v176; // rax
  __int64 v177; // r15
  __int64 v178; // rax
  __int64 v179; // r13
  __int64 v180; // r15
  __int64 v181; // rax
  __int64 v182; // r14
  __int64 v183; // r15
  __int64 v184; // r13
  __int64 v185; // rax
  __int64 v186; // rax
  __int64 v187; // rax
  __int64 v188; // rax
  _UNKNOWN **v189; // r14
  __int64 v190; // r15
  __int64 v191; // r14
  __int64 v192; // r13
  __int64 v193; // rax
  __int64 v194; // rax
  __int64 v195; // r13
  __int64 v196; // rax
  __int64 v197; // r13
  __int64 v198; // rax
  __int64 v199; // r12
  __int64 v200; // r13
  __int64 v201; // rax
  __int64 v202; // r13
  __int64 v203; // rax
  __int64 v204; // r12
  __int64 v205; // r13
  __int64 v206; // rax
  __int64 v207; // r13
  __int64 v208; // rax
  __int64 v209; // r12
  __int64 v210; // r13
  __int64 v211; // rax
  __int64 v212; // r13
  __int64 v213; // rax
  __int64 v214; // r12
  __int64 v215; // r13
  __int64 v216; // rax
  __int64 v217; // r13
  __int64 v218; // rax
  __int64 v219; // r12
  __int64 v220; // r13
  __int64 v221; // rax
  __int64 v222; // r13
  __int64 v223; // rax
  __int64 v224; // r12
  __int64 v225; // r13
  __int64 v226; // rax
  __int64 v227; // r13
  __int64 v228; // rax
  __int64 v229; // r12
  __int64 v230; // r13
  __int64 v231; // rax
  __int64 v232; // r13
  __int64 v233; // rax
  __int64 v234; // r12
  __int64 v235; // r13
  __int64 v236; // rax
  __int64 v237; // r14
  __int64 v238; // r15
  __int64 v239; // r13
  __int64 v240; // rax
  __int64 v241; // rax
  __int64 v242; // rax
  __int64 v243; // r14
  _UNKNOWN **v244; // rdx
  __int64 v245; // rax
  __int64 v246; // rdi
  __int64 v247; // rax
  __int64 v248; // rax
  __int64 v249; // rdi
  __int64 v250; // rax
  __int64 v251; // rdi
  __int64 v252; // rax
  __int64 v253; // rax
  __int64 v254; // rax
  __int64 v255; // rdi
  __int64 v256; // rax
  __int64 v257; // rax
  __int64 v258; // rdi
  __int64 v259; // rax
  __int64 v260; // rdi
  __int64 v261; // rax
  int v262; // eax
  __int64 v263; // rcx
  __int64 v264; // rax
  __int64 v265; // r14
  __int64 v266; // rax
  __int64 v267; // rax
  _UNKNOWN **v268; // rdx
  __int64 v269; // rdi
  __int64 v270; // r14
  __int64 v271; // rax
  __int64 v272; // rax
  __int64 v273; // r14
  __int64 v274; // r15
  __int64 v275; // rax
  __int64 v276; // rax
  int v277; // eax
  __int64 v278; // rcx
  __int64 v279; // rax
  __int64 v280; // r15
  __int64 v281; // rax
  __int64 v282; // r13
  __int64 v283; // r15
  __int64 v284; // rax
  int v285; // eax
  __int64 v286; // rcx
  __int64 v287; // rax
  __int64 v288; // r15
  __int64 v289; // rax
  __int64 v290; // r13
  __int64 v291; // r15
  __int64 v292; // rax
  __int64 v293; // r15
  __int64 v294; // rax
  __int64 v295; // r13
  __int64 v296; // r15
  __int64 v297; // rax
  __int64 v298; // r15
  __int64 v299; // r13
  __int64 v300; // r15
  __int64 v301; // r13
  __int64 v302; // r15
  __int64 v303; // r13
  __int64 v304; // rax
  __int64 v305; // rax
  __int64 v306; // r15
  __int64 v307; // rax
  __int64 v308; // r13
  __int64 v309; // r15
  __int64 v310; // rax
  __int64 v311; // r14
  __int64 v312; // r15
  __int64 v313; // r13
  __int64 v314; // rax
  __int64 v315; // rdi
  __int64 v316; // r14
  __int64 v317; // r15
  __int64 v318; // r14
  __int64 v319; // r13
  __int64 v320; // rax
  __int64 v321; // rax
  __int64 v322; // r14
  __int64 v323; // rcx
  __int64 v324; // rax
  __int64 v325; // r15
  int v326; // eax
  __int64 v327; // r13
  __int64 v328; // rax
  _UNKNOWN **v329; // rax
  __int64 v330; // r14
  __int64 v331; // rcx
  _UNKNOWN **v332; // r15
  __int64 v333; // r13
  __int64 v334; // r15
  __int64 v335; // rdi
  __int64 v336; // rax
  __int64 v337; // rax
  __int64 v338; // r13
  __int64 v339; // rax
  __int64 v340; // r13
  __int64 v341; // rax
  __int64 v342; // r12
  __int64 v343; // r13
  __int64 v344; // rax
  __int64 v345; // r13
  __int64 v346; // rax
  __int64 v347; // r12
  __int64 v348; // r13
  __int64 v349; // rax
  __int64 v350; // r13
  __int64 v351; // rax
  __int64 v352; // r12
  __int64 v353; // r13
  __int64 v354; // rax
  __int64 v355; // r13
  __int64 v356; // rax
  __int64 v357; // r12
  __int64 v358; // r13
  __int64 v359; // rax
  __int64 v360; // r13
  __int64 v361; // rax
  __int64 v362; // r12
  __int64 v363; // r13
  __int64 v364; // rax
  __int64 v365; // r13
  __int64 v366; // rax
  __int64 v367; // r12
  __int64 v368; // r13
  __int64 v369; // rax
  __int64 v370; // r13
  __int64 v371; // rax
  __int64 v372; // r12
  __int64 v373; // r13
  __int64 v374; // rax
  __int64 v375; // r13
  __int64 v376; // rax
  __int64 v377; // r12
  __int64 v378; // r13
  __int64 v379; // r15
  __int64 v380; // r13
  __int64 v381; // r12
  __int64 v382; // rax
  __int64 v383; // r15
  __int64 v384; // r13
  __int64 v385; // r15
  __int64 v386; // r13
  __int64 v387; // rax
  __int64 v388; // rax
  __int64 v389; // rax
  __int64 v390; // rax
  __int64 v391; // r14
  __int64 v392; // r15
  __int64 v393; // r13
  __int64 v394; // rax
  __int64 v395; // rax
  __int64 v396; // rax
  __int64 v397; // rax
  __int64 v398; // rax
  __int64 v399; // rdi
  __int64 v400; // rax
  __int64 v401; // rax
  __int64 v402; // r14
  __int64 v403; // r15
  __int64 v404; // rax
  __int64 v405; // rax
  __int64 v406; // r15
  __int64 v407; // r13
  __int64 v408; // rax
  __int64 v409; // r13
  __int64 v410; // r12
  __int64 v411; // rax
  __int64 v412; // rax
  __int64 v413; // r13
  __int64 v414; // rax
  __int64 v415; // r12
  __int64 v416; // r13
  __int64 v417; // rax
  __int64 v418; // rax
  __int64 v419; // r13
  __int64 v420; // rax
  __int64 v421; // r12
  __int64 v422; // r13
  __int64 v423; // r13
  __int64 v424; // rax
  __int64 v425; // rax
  __int64 v426; // rdi
  __int64 v427; // r15
  __int64 v428; // r13
  __int64 v429; // rax
  __int64 v430; // rcx
  __int64 v431; // rax
  __int64 v432; // rbx
  __int64 v433; // rax
  __int64 v434; // rax
  _QWORD *v435; // rsi
  __int64 *v436; // [rsp+30h] [rbp-3A8h] BYREF
  int v437; // [rsp+38h] [rbp-3A0h]
  __int64 v438; // [rsp+40h] [rbp-398h] BYREF
  int v439; // [rsp+48h] [rbp-390h]
  __int64 v440; // [rsp+50h] [rbp-388h] BYREF
  __int64 v441; // [rsp+58h] [rbp-380h] BYREF
  __int64 v442; // [rsp+60h] [rbp-378h] BYREF
  __int64 v443; // [rsp+68h] [rbp-370h] BYREF
  __int64 v444; // [rsp+70h] [rbp-368h] BYREF
  __int64 v445; // [rsp+78h] [rbp-360h] BYREF
  __int64 v446; // [rsp+80h] [rbp-358h] BYREF
  __int64 v447; // [rsp+88h] [rbp-350h] BYREF
  __int64 v448; // [rsp+90h] [rbp-348h] BYREF
  __int64 v449; // [rsp+98h] [rbp-340h] BYREF
  __int64 v450; // [rsp+A0h] [rbp-338h] BYREF
  __int64 v451; // [rsp+A8h] [rbp-330h] BYREF
  __int64 v452; // [rsp+B0h] [rbp-328h] BYREF
  __int64 v453; // [rsp+B8h] [rbp-320h] BYREF
  __int64 v454; // [rsp+C0h] [rbp-318h] BYREF
  __int64 v455; // [rsp+C8h] [rbp-310h] BYREF
  __int64 v456; // [rsp+D0h] [rbp-308h] BYREF
  __int64 v457; // [rsp+D8h] [rbp-300h] BYREF
  __int64 v458; // [rsp+E0h] [rbp-2F8h] BYREF
  __int64 v459; // [rsp+E8h] [rbp-2F0h] BYREF
  __int64 v460; // [rsp+F0h] [rbp-2E8h] BYREF
  __int64 v461; // [rsp+F8h] [rbp-2E0h] BYREF
  __int64 v462; // [rsp+100h] [rbp-2D8h] BYREF
  __int64 v463; // [rsp+108h] [rbp-2D0h] BYREF
  __int64 v464; // [rsp+110h] [rbp-2C8h] BYREF
  __int64 v465; // [rsp+118h] [rbp-2C0h] BYREF
  __int64 v466; // [rsp+120h] [rbp-2B8h] BYREF
  __int64 v467; // [rsp+128h] [rbp-2B0h] BYREF
  __int64 v468; // [rsp+130h] [rbp-2A8h] BYREF
  __int64 v469; // [rsp+138h] [rbp-2A0h] BYREF
  __int64 v470; // [rsp+140h] [rbp-298h] BYREF
  __int64 v471; // [rsp+148h] [rbp-290h] BYREF
  char v472[8]; // [rsp+150h] [rbp-288h] BYREF
  __int64 v473; // [rsp+158h] [rbp-280h] BYREF
  __int64 v474; // [rsp+160h] [rbp-278h] BYREF
  __int64 v475; // [rsp+168h] [rbp-270h] BYREF
  __int64 v476; // [rsp+170h] [rbp-268h] BYREF
  __int64 v477; // [rsp+178h] [rbp-260h] BYREF
  __int64 v478; // [rsp+180h] [rbp-258h] BYREF
  __int64 v479; // [rsp+188h] [rbp-250h] BYREF
  __int64 v480; // [rsp+190h] [rbp-248h] BYREF
  __int64 v481; // [rsp+198h] [rbp-240h] BYREF
  __int64 v482; // [rsp+1A0h] [rbp-238h] BYREF
  __int64 v483; // [rsp+1A8h] [rbp-230h] BYREF
  __int64 v484; // [rsp+1B0h] [rbp-228h] BYREF
  __int64 v485; // [rsp+1B8h] [rbp-220h] BYREF
  __int64 v486; // [rsp+1C0h] [rbp-218h] BYREF
  __int64 v487; // [rsp+1C8h] [rbp-210h] BYREF
  __int64 v488; // [rsp+1D0h] [rbp-208h] BYREF
  __int64 v489; // [rsp+1D8h] [rbp-200h] BYREF
  __int64 v490; // [rsp+1E0h] [rbp-1F8h] BYREF
  __int64 v491; // [rsp+1E8h] [rbp-1F0h] BYREF
  __int64 v492; // [rsp+1F0h] [rbp-1E8h] BYREF
  __int64 v493; // [rsp+1F8h] [rbp-1E0h] BYREF
  __int64 v494; // [rsp+200h] [rbp-1D8h] BYREF
  __int64 v495; // [rsp+208h] [rbp-1D0h] BYREF
  __int64 v496; // [rsp+210h] [rbp-1C8h] BYREF
  __int64 v497; // [rsp+218h] [rbp-1C0h] BYREF
  __int64 v498; // [rsp+220h] [rbp-1B8h] BYREF
  __int64 v499; // [rsp+228h] [rbp-1B0h] BYREF
  __int64 v500; // [rsp+230h] [rbp-1A8h] BYREF
  __int64 v501; // [rsp+238h] [rbp-1A0h] BYREF
  __int64 v502; // [rsp+240h] [rbp-198h] BYREF
  __int64 v503; // [rsp+248h] [rbp-190h] BYREF
  __int64 v504; // [rsp+250h] [rbp-188h] BYREF
  __int64 v505; // [rsp+258h] [rbp-180h] BYREF
  __int64 v506; // [rsp+260h] [rbp-178h] BYREF
  __int64 v507; // [rsp+268h] [rbp-170h] BYREF
  __int64 v508; // [rsp+270h] [rbp-168h] BYREF
  __int64 v509; // [rsp+278h] [rbp-160h] BYREF
  __int64 v510; // [rsp+280h] [rbp-158h] BYREF
  __int64 v511; // [rsp+288h] [rbp-150h] BYREF
  __int64 v512; // [rsp+290h] [rbp-148h] BYREF
  __int64 v513; // [rsp+298h] [rbp-140h] BYREF
  int n61; // [rsp+2A0h] [rbp-138h] BYREF
  __int64 v515; // [rsp+2A8h] [rbp-130h] BYREF
  __int64 v516; // [rsp+2B0h] [rbp-128h] BYREF
  __int64 v517; // [rsp+2B8h] [rbp-120h] BYREF
  __int64 v518; // [rsp+2C0h] [rbp-118h] BYREF
  __int64 v519; // [rsp+2C8h] [rbp-110h] BYREF
  __int64 v520; // [rsp+2D0h] [rbp-108h] BYREF
  __int64 v521; // [rsp+2D8h] [rbp-100h] BYREF
  __int64 v522; // [rsp+2E0h] [rbp-F8h] BYREF
  __int64 v523; // [rsp+2E8h] [rbp-F0h] BYREF
  __int64 v524; // [rsp+2F0h] [rbp-E8h] BYREF
  __int64 v525; // [rsp+2F8h] [rbp-E0h] BYREF
  __int64 v526; // [rsp+300h] [rbp-D8h] BYREF
  __int64 v527; // [rsp+308h] [rbp-D0h] BYREF
  __int64 v528; // [rsp+310h] [rbp-C8h] BYREF
  __int64 v529; // [rsp+318h] [rbp-C0h] BYREF
  __int64 v530; // [rsp+320h] [rbp-B8h] BYREF
  __int64 v531; // [rsp+328h] [rbp-B0h] BYREF
  __int64 v532; // [rsp+330h] [rbp-A8h] BYREF
  __int64 v533; // [rsp+338h] [rbp-A0h] BYREF
  __int64 v534; // [rsp+340h] [rbp-98h] BYREF
  __int64 v535; // [rsp+348h] [rbp-90h] BYREF
  __int64 v536; // [rsp+350h] [rbp-88h] BYREF
  __int64 v537; // [rsp+358h] [rbp-80h] BYREF
  __int64 v538; // [rsp+360h] [rbp-78h] BYREF
  __int64 v539; // [rsp+368h] [rbp-70h] BYREF
  __int64 v540; // [rsp+370h] [rbp-68h] BYREF
  __int64 v541; // [rsp+378h] [rbp-60h] BYREF
  __int64 v542; // [rsp+380h] [rbp-58h] BYREF
  __int64 v543; // [rsp+388h] [rbp-50h] BYREF
  _QWORD v544[9]; // [rsp+390h] [rbp-48h] BYREF
  __int64 *v545; // [rsp+3E0h] [rbp+8h]

  v1 = 0x1FFFFFFFFFFFFF94LL;
  do
  {
    *(_OWORD *)&v544[v1] = 0;
    *(_OWORD *)&v544[v1 + 2] = 0;
    *(_OWORD *)&v544[v1 + 4] = 0;
    v1 += 6;
  }
  while ( v1 * 8 );
  v544[0] = 0;
  v545 = a1;
  v2 = *a1;
  switch ( *((_DWORD *)a1 + 22) )
  {
    case 0:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      goto LABEL_94;
    case 1:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      goto LABEL_84;
    case 2:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      goto LABEL_68;
    case 3:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      goto LABEL_62;
    case 4:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      goto LABEL_53;
    case 5:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      v8 = a1;
      goto LABEL_44;
    case 6:
      v543 = a1[14];
      a1[14] = 0;
      *((_DWORD *)a1 + 22) = -1;
      v8 = a1;
      goto LABEL_36;
    case 7:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      v8 = a1;
      goto LABEL_27;
    case 8:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      v8 = a1;
      goto LABEL_19;
    case 9:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      goto LABEL_13;
    case 0xA:
      v544[0] = a1[13];
      a1[13] = 0;
      *((_DWORD *)a1 + 22) = -1;
      goto LABEL_5;
    default:
      sub_143028C10(&unk_144CA6E30);
      sub_143028EE0(v545 + 3);
      sub_143028E70(v545[3] + 8, *v545);
      sub_143028E70(v545[3] + 24, v545[1]);
      v115 = sub_141FD15C0(v545[2]);
      v116 = sub_141FD2400(v115, &off_14714CB20, &v542, &v541);
      v117 = 0;
      if ( v116 )
        v117 = v542;
      v542 = 0;
      v118 = sub_141FD15C0(v117);
      sub_141FD2400(v118, &off_146FD6B20, &v540, &v539);
      v540 = 0;
      sub_143028EE0(v545 + 6);
      v119 = sub_141FD15C0(v545[2]);
      v120 = sub_141FD2400(v119, &off_14714CB20, &v538, &v537);
      v121 = 0;
      if ( v120 )
        v121 = v538;
      v538 = 0;
      v122 = sub_141FD15C0(v121);
      sub_141FD2400(v122, &off_14710EA98, &v536, &v535);
      v536 = 0;
      sub_143028EE0(v545 + 7);
      v123 = &off_146FC7388;
      if ( *(_QWORD *)(v2 + 16) )
        v123 = &off_146FC7338;
      *(_QWORD *)(v545[3] + 16) = v123;
      v124 = *(_UNKNOWN ***)(v2 + 72);
      if ( !v124 )
        v124 = &off_147097BA8;
      sub_143028E70(v545[3] + 40, v124);
      v125 = v545[3];
      v126 = sub_140F73490();
      sub_143028E70(v125 + 32, *(_QWORD *)(*(_QWORD *)(v126 + 64) + 80LL));
      v127 = sub_143028C10(&unk_144D7C1E0);
      v128 = sub_143028C10(&unk_144D7C578);
      v129 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v129 + 8) = &off_14723C8B8;
      sub_143028E70(v128 + 8, v129);
      sub_143028E70(v127 + 80, v128);
      v130 = *(_QWORD *)(v2 + 40);
      v131 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v131 + 40, v130);
      *(_DWORD *)(v131 + 48) = 8;
      sub_141ADAE90(v127, &off_146FDA4A0, v131);
      if ( *(&off_1472988D0 - 1) )
        sub_142F8FE64();
      v132 = qword_1472CB138;
      v133 = *(_QWORD *)(qword_1472CB138 + 24);
      v134 = sub_141CF81D0(*(_QWORD *)(v2 + 32), 44, 46);
      v135 = *(_QWORD *)(v132 + 24);
      if ( !v134 )
      {
        sub_141D2DA60(17);
        __debugbreak();
      }
      v136 = v134 + 12;
      v137 = *(_DWORD *)(v134 + 8);
      if ( v135 )
        v138 = sub_141D62740();
      else
        v138 = sub_141D62530();
      v438 = v136;
      v439 = v137;
      if ( !(unsigned int)sub_142D23BA0(&v438, 231, v138, &v534) )
      {
        v438 = v136;
        v439 = v137;
        sub_142D1B270(&v438);
        __debugbreak();
      }
      v139 = sub_143028C10(&unk_144DB87A0);
      *(_QWORD *)(v139 + 8) = v534;
      v533 = v139;
      v436 = &v533;
      v437 = 1;
      v140 = sub_141CF6EA0(v133, (__int64)&off_147193208, (__int64)&v436);
      v141 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v141 + 40, v140);
      *(_DWORD *)(v141 + 48) = 8;
      sub_141ADAE90(v127, &off_146FDA5D8, v141);
      sub_143028EE0(v545 + 8);
      *(_QWORD *)(v545[3] + 48) = 0;
      v142 = sub_143028C10(&unk_144CBDA18);
      *(_QWORD *)(v142 + 104) = &off_146F76688;
      v143 = sub_143028C10(&unk_144D7C578);
      v144 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v144 + 8) = &off_14723C8B8;
      sub_143028E70(v143 + 8, v144);
      sub_143028E70(v142 + 80, v143);
      v145 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v145 + 40) = &off_146DA0CF0;
      *(_DWORD *)(v145 + 48) = 8;
      sub_141ADAE90(v142, &off_147109320, v145);
      v146 = sub_143028C10(&unk_144D7C1E0);
      v147 = sub_143028C10(&unk_144D7C578);
      v148 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v148 + 8) = &off_14723C8B8;
      sub_143028E70(v147 + 8, v148);
      sub_143028E70(v146 + 80, v147);
      v149 = sub_141FD15C0(v545[6]);
      v150 = sub_141FD2400(v149, &off_1470ADED8, &v532, &v531);
      v151 = 0;
      if ( v150 )
        v151 = v532;
      v532 = 0;
      v152 = sub_141FD15C0(v151);
      v153 = 0;
      if ( (unsigned int)sub_141FD2400(v152, &off_1470ADE80, &v530, &v529) )
        v153 = v530;
      v530 = 0;
      if ( v153 )
      {
        v154 = sub_141DC0B60(v153, &off_144A7FC80);
        if ( (v154 & 2) != 0 )
          v155 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v154 - 2))(v153, *(_QWORD *)(v154 + 6));
        else
          v155 = ((__int64 (__fastcall *)(__int64))v154)(v153);
      }
      else
      {
        v155 = 0;
      }
      v156 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v156 + 40, v155);
      *(_DWORD *)(v156 + 48) = 8;
      sub_141ADAE90(v146, &off_1470ADE80, v156);
      v157 = sub_141FD15C0(v545[6]);
      v158 = sub_141FD2400(v157, &off_1470ADED8, &v528, &v527);
      v159 = 0;
      if ( v158 )
        v159 = v528;
      v528 = 0;
      v160 = sub_141FD15C0(v159);
      v161 = 0;
      if ( (unsigned int)sub_141FD2400(v160, &off_1470ADEA8, &v526, &v525) )
        v161 = v526;
      v526 = 0;
      if ( v161 )
      {
        v162 = sub_141DC0B60(v161, &off_144A7FC80);
        if ( (v162 & 2) != 0 )
          v163 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v162 - 2))(v161, *(_QWORD *)(v162 + 6));
        else
          v163 = ((__int64 (__fastcall *)(__int64))v162)(v161);
      }
      else
      {
        v163 = 0;
      }
      v164 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v164 + 40, v163);
      *(_DWORD *)(v164 + 48) = 8;
      sub_141ADAE90(v146, &off_1470ADEA8, v164);
      v165 = sub_141FD15C0(v545[6]);
      v166 = 0;
      if ( (unsigned int)sub_141FD2400(v165, &off_14714A4B8, &v524, &v523) )
        v166 = v524;
      v524 = 0;
      if ( v166 )
      {
        v167 = sub_141DC0B60(v166, &off_144A7FC80);
        if ( (v167 & 2) != 0 )
          v168 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v167 - 2))(v166, *(_QWORD *)(v167 + 6));
        else
          v168 = ((__int64 (__fastcall *)(__int64))v167)(v166);
      }
      else
      {
        v168 = 0;
      }
      v169 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v169 + 40, v168);
      *(_DWORD *)(v169 + 48) = 8;
      sub_141ADAE90(v146, &off_14714A4B8, v169);
      v170 = sub_141FD15C0(v545[7]);
      v171 = 0;
      if ( (unsigned int)sub_141FD2400(v170, &off_146F90DD8, &v522, &v521) )
        v171 = v522;
      v522 = 0;
      if ( v171 )
      {
        v172 = sub_141DC0B60(v171, &off_144A7FC80);
        if ( (v172 & 2) != 0 )
          v173 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v172 - 2))(v171, *(_QWORD *)(v172 + 6));
        else
          v173 = ((__int64 (__fastcall *)(__int64))v172)(v171);
      }
      else
      {
        v173 = 0;
      }
      v174 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v174 + 40, v173);
      *(_DWORD *)(v174 + 48) = 8;
      sub_141ADAE90(v146, &off_146FBFFF0, v174);
      v175 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v175 + 40) = &off_146E312C8;
      *(_DWORD *)(v175 + 48) = 8;
      sub_141ADAE90(v146, &off_146F7C598, v175);
      v176 = sub_141FD15C0(v545[7]);
      v177 = 0;
      if ( (unsigned int)sub_141FD2400(v176, &off_147175AA8, &v520, &v519) )
        v177 = v520;
      v520 = 0;
      if ( v177 )
      {
        v178 = sub_141DC0B60(v177, &off_144A7FC80);
        if ( (v178 & 2) != 0 )
          v179 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v178 - 2))(v177, *(_QWORD *)(v178 + 6));
        else
          v179 = ((__int64 (__fastcall *)(__int64))v178)(v177);
      }
      else
      {
        v179 = 0;
      }
      v180 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v180 + 40, v179);
      *(_DWORD *)(v180 + 48) = 8;
      sub_141ADAE90(v146, &off_146FC0600, v180);
      sub_141ADAE90(v142, &off_14717D2E8, v146);
      v181 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v181 + 40) = &off_1471213F8;
      *(_DWORD *)(v181 + 48) = 8;
      sub_141ADAE90(v142, &off_14711CCB0, v181);
      v182 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
      v183 = sub_143028C10(&unk_144BDF900);
      sub_1408C22E0(v183, &off_147097F60);
      v184 = sub_143028C10(&unk_144FE9240);
      sub_142FBFD34(v184, v545[3]);
      v544[0] = sub_1408B6310(v182, v183, v142, v184);
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)v545 + 22) = 0;
        sub_143028EE0(v545 + 13);
        v185 = sub_142C76FA0(v545, v545 + 12);
        return sub_142D72040(&off_1449B5288, v544, v185);
      }
LABEL_94:
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v544[0], 0);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_461;
      v46 = v545;
      v109 = *(_QWORD *)(v545[3] + 48);
      if ( !v109 || !*(_DWORD *)(v109 + 8) )
        goto LABEL_72;
      sub_143028C10(&unk_144CA7510);
      sub_143028EE0(v545 + 4);
      sub_143028E70(v545[4] + 24, v545[3]);
      *(_QWORD *)(v545[4] + 16) = 0;
      *(_QWORD *)(v545[4] + 8) = 0;
      v110 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
      v111 = sub_141FD15C0(v545[6]);
      v112 = sub_141FD2400(v111, &off_147003A88, &v518, &v517);
      v113 = 0;
      if ( v112 )
        v113 = v518;
      v518 = 0;
      if ( v113 )
      {
        v186 = sub_141FD15C0(v113);
        v114 = 0;
        if ( (unsigned int)sub_141FD2400(v186, &off_1470494A8, &v516, &v515) )
          v114 = v516;
        v516 = 0;
      }
      else
      {
        v114 = 0;
      }
      if ( v114 )
      {
        v187 = sub_141DC0B60(v114, &off_144A7FC80);
        if ( (v187 & 2) != 0 )
          v188 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v187 - 2))(v114, *(_QWORD *)(v187 + 6));
        else
          v188 = ((__int64 (__fastcall *)(__int64))v187)(v114);
        v189 = (_UNKNOWN **)v188;
      }
      else
      {
        v189 = nullptr;
      }
      if ( !v189 )
        v189 = &off_1470985E8;
      v190 = sub_143028C10(&unk_144BDF900);
      sub_1408C22E0(v190, v189);
      v191 = sub_143028C10(&unk_144CB7DE8);
      sub_14130C960(v191);
      sub_14130CC50(v191, &off_146DD3A08, *(_QWORD *)(*(_QWORD *)(v545[4] + 24) + 48LL));
      v192 = sub_143028C10(&unk_144FE9240);
      sub_142FBFDD0(v192, v545[4]);
      v544[0] = sub_1408B6310(v110, v190, v191, v192);
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)v545 + 22) = 1;
        sub_143028EE0(v545 + 13);
        v193 = sub_142C76FA0(v545, v545 + 12);
        return sub_142D72040(&off_1449B5288, v544, v193);
      }
LABEL_84:
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v544[0], 0);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_461;
      v46 = v545;
      v93 = *(_QWORD *)(v545[4] + 16);
      if ( v93 && *(_DWORD *)(v93 + 8) )
      {
        v94 = sub_143028C10(&unk_144D7C1E0);
        if ( off_147298AD8[-1] )
          sub_142F900F8();
        v95 = *(_QWORD *)(qword_1472CB278 + 8);
        v96 = sub_143028C10(&unk_144D7C578);
        v97 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v97 + 8) = &off_14723C8B8;
        sub_143028E70(v96 + 8, v97);
        sub_143028E70(v94 + 80, v96);
        v98 = *(_QWORD *)(v545[4] + 16);
        v99 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v99 + 40, v98);
        *(_DWORD *)(v99 + 48) = 8;
        sub_141ADAE90(v94, &off_14716D5F8, v99);
        v100 = sub_141ADD070(v94, 0);
        v101 = sub_141E166A0(v95, v100);
        v102 = sub_141D09B60(v101);
        n61 = 61;
        v103 = sub_141CFA600(v102, &n61, 1, 2);
        v104 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
        v105 = sub_143028C10(&unk_144BDF900);
        sub_1408C22E0(v105, &off_147098740);
        v106 = sub_143028C10(&unk_144CB7DE8);
        sub_14130C960(v106);
        sub_14130CC50(v106, &off_14716D3D0, v103);
        v107 = sub_143028C10(&unk_144FE9240);
        sub_142FBFDE8(v107, v545[4]);
        v544[0] = sub_1408B6310(v104, v105, v106, v107);
        a1 = v545;
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
        {
          *((_DWORD *)v545 + 22) = 2;
          sub_143028EE0(v545 + 13);
          v108 = sub_142C76FA0(v545, v545 + 12);
          return sub_142D72040(&off_1449B5288, v544, v108);
        }
LABEL_68:
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
        {
          sub_141DC8280(v544[0], 0);
          a1 = v545;
        }
        v46 = a1;
      }
      v46[4] = 0;
LABEL_72:
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_461;
      *(_QWORD *)(v46[3] + 56LL) = 0;
      v47 = sub_143028C10(&unk_144CBDA18);
      *(_QWORD *)(v47 + 104) = &off_146F76688;
      v48 = sub_143028C10(&unk_144D7C578);
      v49 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v49 + 8) = &off_14723C8B8;
      sub_143028E70(v48 + 8, v49);
      sub_143028E70(v47 + 80, v48);
      v50 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v50 + 40) = &off_146EEF8F0;
      *(_DWORD *)(v50 + 48) = 8;
      sub_141ADAE90(v47, &off_147109320, v50);
      v51 = sub_143028C10(&unk_144D7C1E0);
      v52 = sub_143028C10(&unk_144D7C578);
      v53 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v53 + 8) = &off_14723C8B8;
      sub_143028E70(v52 + 8, v53);
      sub_143028E70(v51 + 80, v52);
      v54 = *(_QWORD *)(v2 + 24);
      v55 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v55 + 40, v54);
      *(_DWORD *)(v55 + 48) = 8;
      sub_141ADAE90(v51, &off_147171D48, v55);
      v56 = sub_143028C10(&unk_144D7C1E0);
      v57 = sub_143028C10(&unk_144D7C578);
      v58 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v58 + 8) = &off_14723C8B8;
      sub_143028E70(v57 + 8, v58);
      sub_143028E70(v56 + 80, v57);
      v59 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v59 + 40) = &off_146DA8128;
      *(_DWORD *)(v59 + 48) = 8;
      sub_141ADAE90(v56, &off_147117428, v59);
      v60 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v60 + 40) = &off_146D00F38;
      *(_DWORD *)(v60 + 48) = 8;
      sub_141ADAE90(v56, &off_147117308, v60);
      sub_141ADAE90(v51, &off_147117368, v56);
      v61 = sub_143028C10(&unk_144D7C1E0);
      v62 = sub_143028C10(&unk_144D7C578);
      v63 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v63 + 8) = &off_14723C8B8;
      sub_143028E70(v62 + 8, v63);
      sub_143028E70(v61 + 80, v62);
      v64 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v64 + 40) = &off_146F5FF08;
      *(_DWORD *)(v64 + 48) = 8;
      sub_141ADAE90(v61, &off_147184E58, v64);
      v65 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v65 + 40) = &off_14727D118;
      *(_DWORD *)(v65 + 48) = 9;
      sub_141ADAE90(v61, &off_1470ACAF8, v65);
      v66 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v66 + 40) = &off_14701B338;
      *(_DWORD *)(v66 + 48) = 8;
      sub_141ADAE90(v61, &off_1470B0BD8, v66);
      v67 = sub_143028C10(&unk_144D7CCC0);
      v68 = sub_141AAF6B0(24);
      sub_143028E70(v67 + 40, v68);
      *(_DWORD *)(v67 + 48) = 6;
      sub_141ADAE90(v61, &off_146FD3A30, v67);
      v69 = sub_143028C10(&unk_144D7CCC0);
      v70 = sub_141AAF6B0(785);
      sub_143028E70(v69 + 40, v70);
      *(_DWORD *)(v69 + 48) = 6;
      sub_141ADAE90(v61, &off_1471530D0, v69);
      v71 = sub_143028C10(&unk_144D7CCC0);
      v72 = sub_141AAF6B0(581);
      sub_143028E70(v71 + 40, v72);
      *(_DWORD *)(v71 + 48) = 6;
      sub_141ADAE90(v61, &off_147153188, v71);
      if ( qword_147298868[-1] )
        sub_142F8FDE0();
      v73 = qword_1472CB100;
      v74 = *(_QWORD *)(*(_QWORD *)(qword_1472CB100 + 16) + 8LL);
      if ( !v74 )
        v74 = sub_141E087E0();
      v75 = sub_141D0D640();
      v76 = 0;
      v76.m128d_f64[0] = (double)(int)sub_141D30960(v74, v75, 2, *(_QWORD *)(v73 + 16)) / -600000000.0;
      n0x7FFFFFFF = 0x7FFFFFFF;
      n0x7FFFFFFF_1 = (int)COERCE_DOUBLE(*(_QWORD *)&_mm_cmpord_sd(v76, v76).m128d_f64[0] & *(_QWORD *)&v76.m128d_f64[0]);
      if ( v76.m128d_f64[0] < 2147483648.0 )
        n0x7FFFFFFF = n0x7FFFFFFF_1;
      n0x7FFFFFFF_2 = n0x7FFFFFFF;
      v80 = sub_143028C10(&unk_144D7CCC0);
      v81 = sub_141AAF6B0(n0x7FFFFFFF_2);
      sub_143028E70(v80 + 40, v81);
      *(_DWORD *)(v80 + 48) = 6;
      sub_141ADAE90(v61, &off_14716E280, v80);
      sub_141ADAE90(v51, &off_146F9C440, v61);
      v82 = v46[8];
      v83 = sub_143028C10(&unk_144D7C1E0);
      v84 = sub_143028C10(&unk_144D7C578);
      v85 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v85 + 8) = &off_14723C8B8;
      sub_143028E70(v84 + 8, v85);
      sub_143028E70(v83 + 80, v84);
      sub_141AD80A0(v83, v82, 0);
      sub_141ADAE90(v51, &off_146F71A38, v83);
      v86 = sub_143028C10(&unk_144D7C1E0);
      v87 = sub_143028C10(&unk_144D7C578);
      v88 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v88 + 8) = &off_14723C8B8;
      sub_143028E70(v87 + 8, v88);
      sub_143028E70(v86 + 80, v87);
      v89 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v89 + 40) = &off_146DA8128;
      *(_DWORD *)(v89 + 48) = 8;
      sub_141ADAE90(v86, &off_147036118, v89);
      v90 = sub_141FD15C0(v46[7]);
      v91 = 0;
      if ( (unsigned int)sub_141FD2400(v90, &off_14709FB80, &v513, &v512) )
        v91 = v513;
      v513 = 0;
      if ( v91 )
      {
        v194 = sub_141DC0B60(v91, &off_144A7FC80);
        if ( (v194 & 2) != 0 )
          v92 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v194 - 2))(v91, *(_QWORD *)(v194 + 6));
        else
          v92 = ((__int64 (__fastcall *)(__int64))v194)(v91);
      }
      else
      {
        v92 = 0;
      }
      v195 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v195 + 40, v92);
      *(_DWORD *)(v195 + 48) = 8;
      sub_141ADAE90(v86, &off_146FD8F48, v195);
      v196 = sub_141FD15C0(v46[7]);
      v197 = 0;
      if ( (unsigned int)sub_141FD2400(v196, &off_147175AA8, &v511, &v510) )
        v197 = v511;
      v511 = 0;
      if ( v197 )
      {
        v198 = sub_141DC0B60(v197, &off_144A7FC80);
        if ( (v198 & 2) != 0 )
          v199 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v198 - 2))(v197, *(_QWORD *)(v198 + 6));
        else
          v199 = ((__int64 (__fastcall *)(__int64))v198)(v197);
      }
      else
      {
        v199 = 0;
      }
      v200 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v200 + 40, v199);
      *(_DWORD *)(v200 + 48) = 8;
      sub_141ADAE90(v86, &off_146FC0018, v200);
      v201 = sub_141FD15C0(v46[7]);
      v202 = 0;
      if ( (unsigned int)sub_141FD2400(v201, &off_146FC04B0, &v509, &v508) )
        v202 = v509;
      v509 = 0;
      if ( v202 )
      {
        v203 = sub_141DC0B60(v202, &off_144A7FC80);
        if ( (v203 & 2) != 0 )
          v204 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v203 - 2))(v202, *(_QWORD *)(v203 + 6));
        else
          v204 = ((__int64 (__fastcall *)(__int64))v203)(v202);
      }
      else
      {
        v204 = 0;
      }
      v205 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v205 + 40, v204);
      *(_DWORD *)(v205 + 48) = 8;
      sub_141ADAE90(v86, &off_146FC0628, v205);
      v206 = sub_141FD15C0(v46[7]);
      v207 = 0;
      if ( (unsigned int)sub_141FD2400(v206, &off_1470218F8, &v507, &v506) )
        v207 = v507;
      v507 = 0;
      if ( v207 )
      {
        v208 = sub_141DC0B60(v207, &off_144A7FC80);
        if ( (v208 & 2) != 0 )
          v209 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v208 - 2))(v207, *(_QWORD *)(v208 + 6));
        else
          v209 = ((__int64 (__fastcall *)(__int64))v208)(v207);
      }
      else
      {
        v209 = 0;
      }
      v210 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v210 + 40, v209);
      *(_DWORD *)(v210 + 48) = 8;
      sub_141ADAE90(v86, &off_147021820, v210);
      v211 = sub_141FD15C0(v46[7]);
      v212 = 0;
      if ( (unsigned int)sub_141FD2400(v211, &off_1470218C8, &v505, &v504) )
        v212 = v505;
      v505 = 0;
      if ( v212 )
      {
        v213 = sub_141DC0B60(v212, &off_144A7FC80);
        if ( (v213 & 2) != 0 )
          v214 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v213 - 2))(v212, *(_QWORD *)(v213 + 6));
        else
          v214 = ((__int64 (__fastcall *)(__int64))v213)(v212);
      }
      else
      {
        v214 = 0;
      }
      v215 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v215 + 40, v214);
      *(_DWORD *)(v215 + 48) = 8;
      sub_141ADAE90(v86, &off_1470217B0, v215);
      v216 = sub_141FD15C0(v46[6]);
      v217 = 0;
      if ( (unsigned int)sub_141FD2400(v216, &off_14714A4B8, &v503, &v502) )
        v217 = v503;
      v503 = 0;
      if ( v217 )
      {
        v218 = sub_141DC0B60(v217, &off_144A7FC80);
        if ( (v218 & 2) != 0 )
          v219 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v218 - 2))(v217, *(_QWORD *)(v218 + 6));
        else
          v219 = ((__int64 (__fastcall *)(__int64))v218)(v217);
      }
      else
      {
        v219 = 0;
      }
      v220 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v220 + 40, v219);
      *(_DWORD *)(v220 + 48) = 8;
      sub_141ADAE90(v86, &off_14716D588, v220);
      v221 = sub_141FD15C0(v46[7]);
      v222 = 0;
      if ( (unsigned int)sub_141FD2400(v221, &off_14701D188, &v501, &v500) )
        v222 = v501;
      v501 = 0;
      if ( v222 )
      {
        v223 = sub_141DC0B60(v222, &off_144A7FC80);
        if ( (v223 & 2) != 0 )
          v224 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v223 - 2))(v222, *(_QWORD *)(v223 + 6));
        else
          v224 = ((__int64 (__fastcall *)(__int64))v223)(v222);
      }
      else
      {
        v224 = 0;
      }
      v225 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v225 + 40, v224);
      *(_DWORD *)(v225 + 48) = 8;
      sub_141ADAE90(v86, &off_14701CFA8, v225);
      v226 = sub_141FD15C0(v46[6]);
      v227 = 0;
      if ( (unsigned int)sub_141FD2400(v226, &off_1471492E8, &v499, &v498) )
        v227 = v499;
      v499 = 0;
      if ( v227 )
      {
        v228 = sub_141DC0B60(v227, &off_144A7FC80);
        if ( (v228 & 2) != 0 )
          v229 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v228 - 2))(v227, *(_QWORD *)(v228 + 6));
        else
          v229 = ((__int64 (__fastcall *)(__int64))v228)(v227);
      }
      else
      {
        v229 = 0;
      }
      v230 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v230 + 40, v229);
      *(_DWORD *)(v230 + 48) = 8;
      sub_141ADAE90(v86, &off_14716D260, v230);
      v231 = sub_141FD15C0(v46[6]);
      v232 = 0;
      if ( (unsigned int)sub_141FD2400(v231, &off_147160DE0, &v497, &v496) )
        v232 = v497;
      v497 = 0;
      if ( v232 )
      {
        v233 = sub_141DC0B60(v232, &off_144A7FC80);
        if ( (v233 & 2) != 0 )
          v234 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v233 - 2))(v232, *(_QWORD *)(v233 + 6));
        else
          v234 = ((__int64 (__fastcall *)(__int64))v233)(v232);
      }
      else
      {
        v234 = 0;
      }
      v235 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v235 + 40, v234);
      *(_DWORD *)(v235 + 48) = 8;
      sub_141ADAE90(v86, &off_14716D2A8, v235);
      sub_141ADAE90(v51, &off_14716D9A0, v86);
      sub_141ADAE90(v47, &off_14717D2E8, v51);
      v236 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v236 + 40) = &off_1470E2CC0;
      *(_DWORD *)(v236 + 48) = 8;
      sub_141ADAE90(v47, &off_14711CCB0, v236);
      v237 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
      v238 = sub_143028C10(&unk_144BDF900);
      sub_1408C22E0(v238, &off_147098170);
      v239 = sub_143028C10(&unk_144FE9240);
      sub_142FBFD4C(v239, v46[3]);
      v544[0] = sub_1408B6310(v237, v238, v47, v239);
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)v545 + 22) = 3;
        sub_143028EE0(v545 + 13);
        v240 = sub_142C76FA0(v545, v545 + 12);
        return sub_142D72040(&off_1449B5288, v544, v240);
      }
LABEL_62:
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v544[0], 0);
      if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
        goto LABEL_461;
      v5 = v545;
      v44 = *(_QWORD *)(v545[3] + 56);
      if ( v44 )
      {
        v241 = sub_141FD15C0(v44);
        v45 = 0;
        if ( (unsigned int)sub_141FD2400(v241, &off_14716D6C8, &v495, &v494) )
          v45 = v495;
        v495 = 0;
      }
      else
      {
        v45 = 0;
      }
      if ( v45 )
      {
        v242 = sub_141DC0B60(v45, &off_144A7FC80);
        if ( (v242 & 2) != 0 )
          v243 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v242 - 2))(v45, *(_QWORD *)(v242 + 6));
        else
          v243 = ((__int64 (*)(void))v242)();
      }
      else
      {
        v243 = 0;
      }
      if ( (unsigned int)sub_141CF4290(v243, &off_146B67428) )
      {
        sub_143028C10(&unk_144CA78F8);
        sub_143028EE0(v545 + 5);
        sub_143028E70(v545[5] + 72, v545[3]);
        v254 = sub_141FD15C0(*(_QWORD *)(*(_QWORD *)(v545[5] + 72) + 56LL));
        v255 = 0;
        if ( (unsigned int)sub_141FD2400(v254, &off_14716D7B0, &v493, &v492) )
          v255 = v493;
        v493 = 0;
        if ( v255 )
        {
          v256 = sub_141DC0B60(v255, &off_144A7FC80);
          if ( (v256 & 2) != 0 )
            (*(void (__fastcall **)(__int64, _QWORD))(v256 - 2))(v255, *(_QWORD *)(v256 + 6));
          else
            ((void (__fastcall *)(__int64))v256)(v255);
        }
        sub_143028EE0(v545 + 9);
        v257 = sub_141FD15C0(*(_QWORD *)(*(_QWORD *)(v545[5] + 72) + 56LL));
        v258 = 0;
        if ( (unsigned int)sub_141FD2400(v257, &off_14710EA18, &v491, &v490) )
          v258 = v491;
        v491 = 0;
        if ( v258 )
        {
          v259 = sub_141DC0B60(v258, &off_144A7FC80);
          if ( (v259 & 2) != 0 )
            (*(void (__fastcall **)(__int64, _QWORD))(v259 - 2))(v258, *(_QWORD *)(v259 + 6));
          else
            ((void (__fastcall *)(__int64))v259)(v258);
        }
        sub_143028EE0(v545 + 10);
        v260 = v545[5];
        v261 = sub_141FD15C0(*(_QWORD *)(*(_QWORD *)(v260 + 72) + 56LL));
        v262 = sub_141FD2400(v261, &off_14714A000, &v489, &v488);
        v263 = 0;
        if ( v262 )
          v263 = v489;
        v489 = 0;
        if ( v263 )
        {
          v264 = sub_141FD15C0(v263);
          v265 = 0;
          if ( (unsigned int)sub_141FD2400(v264, &off_1470494A8, &v487, &v486) )
            v265 = v487;
          v487 = 0;
        }
        else
        {
          v265 = 0;
        }
        if ( v265 )
        {
          v266 = sub_141DC0B60(v265, &off_144A7FC80);
          if ( (v266 & 2) != 0 )
            v267 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v266 - 2))(v265, *(_QWORD *)(v266 + 6));
          else
            v267 = ((__int64 (*)(void))v266)();
          v268 = (_UNKNOWN **)v267;
        }
        else
        {
          v268 = nullptr;
        }
        if ( !v268 )
          v268 = &off_147098540;
        sub_143028E70(v260 + 56, v268);
        *(_QWORD *)(v545[5] + 8) = 0;
        v269 = sub_143028C10(&unk_144CBDA18);
        *(_QWORD *)(v269 + 104) = &off_146F76688;
        v270 = sub_143028C10(&unk_144D7C578);
        v271 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v271 + 8) = &off_14723C8B8;
        sub_143028E70(v270 + 8, v271);
        sub_143028E70(v269 + 80, v270);
        v272 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v272 + 40) = &off_146DA0CF0;
        *(_DWORD *)(v272 + 48) = 8;
        sub_141ADAE90(v269, &off_147109320, v272);
        v273 = sub_143028C10(&unk_144D7C1E0);
        v274 = sub_143028C10(&unk_144D7C578);
        v275 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v275 + 8) = &off_14723C8B8;
        sub_143028E70(v274 + 8, v275);
        sub_143028E70(v273 + 80, v274);
        v276 = sub_141FD15C0(v545[6]);
        v277 = sub_141FD2400(v276, &off_1470ADED8, &v485, &v484);
        v278 = 0;
        if ( v277 )
          v278 = v485;
        v485 = 0;
        v279 = sub_141FD15C0(v278);
        v280 = 0;
        if ( (unsigned int)sub_141FD2400(v279, &off_1470ADE80, &v483, &v482) )
          v280 = v483;
        v483 = 0;
        if ( v280 )
        {
          v281 = sub_141DC0B60(v280, &off_144A7FC80);
          if ( (v281 & 2) != 0 )
            v282 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v281 - 2))(v280, *(_QWORD *)(v281 + 6));
          else
            v282 = ((__int64 (__fastcall *)(__int64))v281)(v280);
        }
        else
        {
          v282 = 0;
        }
        v283 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v283 + 40, v282);
        *(_DWORD *)(v283 + 48) = 8;
        sub_141ADAE90(v273, &off_1470ADE80, v283);
        v284 = sub_141FD15C0(v545[6]);
        v285 = sub_141FD2400(v284, &off_1470ADED8, &v481, &v480);
        v286 = 0;
        if ( v285 )
          v286 = v481;
        v481 = 0;
        v287 = sub_141FD15C0(v286);
        v288 = 0;
        if ( (unsigned int)sub_141FD2400(v287, &off_1470ADEA8, &v479, &v478) )
          v288 = v479;
        v479 = 0;
        if ( v288 )
        {
          v289 = sub_141DC0B60(v288, &off_144A7FC80);
          if ( (v289 & 2) != 0 )
            v290 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v289 - 2))(v288, *(_QWORD *)(v289 + 6));
          else
            v290 = ((__int64 (__fastcall *)(__int64))v289)(v288);
        }
        else
        {
          v290 = 0;
        }
        v291 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v291 + 40, v290);
        *(_DWORD *)(v291 + 48) = 8;
        sub_141ADAE90(v273, &off_1470ADEA8, v291);
        v292 = sub_141FD15C0(v545[6]);
        v293 = 0;
        if ( (unsigned int)sub_141FD2400(v292, &off_14714A4B8, &v477, &v476) )
          v293 = v477;
        v477 = 0;
        if ( v293 )
        {
          v294 = sub_141DC0B60(v293, &off_144A7FC80);
          if ( (v294 & 2) != 0 )
            v295 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v294 - 2))(v293, *(_QWORD *)(v294 + 6));
          else
            v295 = ((__int64 (__fastcall *)(__int64))v294)(v293);
        }
        else
        {
          v295 = 0;
        }
        v296 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v296 + 40, v295);
        *(_DWORD *)(v296 + 48) = 8;
        sub_141ADAE90(v273, &off_14714A4B8, v296);
        v297 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v297 + 40) = &off_147097D08;
        *(_DWORD *)(v297 + 48) = 8;
        sub_141ADAE90(v273, &off_14714DB10, v297);
        v298 = *(_QWORD *)(v545[5] + 56);
        v299 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v299 + 40, v298);
        *(_DWORD *)(v299 + 48) = 8;
        sub_141ADAE90(v273, &off_14714A060, v299);
        v300 = v545[9];
        v301 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v301 + 40, v300);
        *(_DWORD *)(v301 + 48) = 8;
        sub_141ADAE90(v273, &off_147173188, v301);
        v302 = v545[10];
        v303 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v303 + 40, v302);
        *(_DWORD *)(v303 + 48) = 8;
        sub_141ADAE90(v273, &off_14710EA18, v303);
        v304 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v304 + 40) = &off_146E312C8;
        *(_DWORD *)(v304 + 48) = 8;
        sub_141ADAE90(v273, &off_146F7C598, v304);
        v305 = sub_141FD15C0(v545[7]);
        v306 = 0;
        if ( (unsigned int)sub_141FD2400(v305, &off_147175AA8, &v475, &v474) )
          v306 = v475;
        v475 = 0;
        if ( v306 )
        {
          v307 = sub_141DC0B60(v306, &off_144A7FC80);
          if ( (v307 & 2) != 0 )
            v308 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v307 - 2))(v306, *(_QWORD *)(v307 + 6));
          else
            v308 = ((__int64 (__fastcall *)(__int64))v307)(v306);
        }
        else
        {
          v308 = 0;
        }
        v309 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v309 + 40, v308);
        *(_DWORD *)(v309 + 48) = 8;
        sub_141ADAE90(v273, &off_146FC0600, v309);
        sub_141ADAE90(v269, &off_14717D2E8, v273);
        v310 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v310 + 40) = &off_1471213F8;
        *(_DWORD *)(v310 + 48) = 8;
        sub_141ADAE90(v269, &off_14711CCB0, v310);
        v311 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
        v312 = sub_143028C10(&unk_144BDF900);
        sub_1408C22E0(v312, &off_147097F60);
        v313 = sub_143028C10(&unk_144FE9240);
        sub_142FBFE24(v313, v545[5]);
        v544[0] = sub_1408B6310(v311, v312, v269, v313);
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
        {
          *((_DWORD *)v545 + 22) = 4;
          sub_143028EE0(v545 + 13);
          v314 = sub_142C76FA0(v545, v545 + 12);
          return sub_142D72040(&off_1449B5288, v544, v314);
        }
LABEL_53:
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v544[0], 0);
        if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
          goto LABEL_461;
        v8 = v545;
        v42 = v545[5];
        v43 = *(_QWORD *)(v42 + 8);
        if ( !v43 || !*(_DWORD *)(v43 + 8) )
        {
          v37 = *(_QWORD *)(v2 + 8);
          v38 = &off_146AEC898;
          if ( !*(_BYTE *)(v2 + 144) )
            v38 = &off_146E3A158;
LABEL_60:
          sub_140F9EFA0(v37, v38, &off_147149C08);
          goto LABEL_461;
        }
        *(_QWORD *)(v42 + 16) = 0;
        *(_QWORD *)(v545[5] + 24) = 0;
        v315 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
        v316 = *(_QWORD *)(v545[5] + 56);
        v317 = sub_143028C10(&unk_144BDF900);
        sub_1408C22E0(v317, v316);
        v318 = sub_143028C10(&unk_144CB7DE8);
        sub_14130C960(v318);
        sub_14130CC50(v318, &off_146DD3A08, *(_QWORD *)(v545[5] + 8));
        sub_14130CC50(v318, &off_146DF88D0, *(_QWORD *)(v2 + 24));
        v319 = sub_143028C10(&unk_144FE9240);
        sub_142FBFE3C(v319, v545[5]);
        v544[0] = sub_1408B6310(v315, v317, v318, v319);
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
        {
          *((_DWORD *)v545 + 22) = 5;
          sub_143028EE0(v545 + 13);
          v320 = sub_142C76FA0(v545, v545 + 12);
          return sub_142D72040(&off_1449B5288, v544, v320);
        }
LABEL_44:
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v544[0], 0);
        if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
          goto LABEL_461;
        v39 = v8[5];
        v40 = *(_QWORD *)(v39 + 16);
        if ( !v40 || !*(_DWORD *)(v40 + 8) || (v41 = *(_QWORD *)(v39 + 24)) == 0 )
        {
          v37 = *(_QWORD *)(v2 + 8);
          v38 = &off_146AEC898;
          if ( !*(_BYTE *)(v2 + 144) )
            v38 = &off_146E3A108;
          goto LABEL_60;
        }
        v543 = sub_1408A2FA0(*(_QWORD *)(v2 + 8), *(_QWORD *)(v39 + 16), v41, 0);
        if ( (*(_DWORD *)(v543 + 52) & 0x1600000) == 0 )
        {
          *((_DWORD *)v8 + 22) = 6;
          sub_143028EE0(v8 + 14);
          v321 = sub_142C76FA0(v8, v8 + 12);
          return sub_142D72040(&off_1449C6C60, &v543, v321);
        }
LABEL_36:
        if ( (*(_DWORD *)(v543 + 52) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v543, 0);
        v36 = *(_QWORD *)(v543 + 56);
        if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
          goto LABEL_461;
        if ( !v36 || !*(_QWORD *)(v36 + 16) )
        {
          v37 = *(_QWORD *)(v2 + 8);
          v38 = &off_146AEC898;
          if ( !*(_BYTE *)(v2 + 144) )
            v38 = &off_146E3A090;
          goto LABEL_60;
        }
        v322 = v8[5];
        v323 = *(_QWORD *)(v322 + 16);
        if ( v323 )
        {
          v473 = 0;
          v472[0] = 0;
          v324 = sub_141E5C8C0(v323, 0, 1, &v473, v472);
          v325 = v324;
          if ( !v473 )
          {
            v326 = sub_141E552B0(v324, 0);
            goto LABEL_333;
          }
        }
        else
        {
          v325 = 0;
        }
        v326 = 0;
LABEL_333:
        v473 = 0;
        if ( v326 )
        {
          v327 = sub_141E54750();
          v328 = sub_141E541B0(v325);
          v329 = (_UNKNOWN **)sub_141CF62D0(v327, &off_146B1D838, v328);
        }
        else
        {
          v329 = &off_147097BA8;
        }
        sub_143028E70(v322 + 32, v329);
        *(_QWORD *)(v8[5] + 40) = 0;
        *(_QWORD *)(v8[5] + 48) = 0;
        v330 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
        v331 = *(_QWORD *)(v36 + 8);
        if ( v331 )
          v332 = (_UNKNOWN **)(*(__int64 (__fastcall **)(__int64))(*(_QWORD *)v331 + 24LL))(v331);
        else
          v332 = nullptr;
        if ( !v332 )
          v332 = sub_141CF6230((__int64)&off_147098688, v8[9]);
        v333 = sub_143028C10(&unk_144BDF900);
        sub_1408C22E0(v333, v332);
        v334 = sub_143028C10(&unk_144FE9240);
        v335 = *(_QWORD *)(v36 + 16);
        sub_142FBFE54(v334, v8[5]);
        v544[0] = sub_1408B6310(v330, v333, v335, v334);
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
        {
          *((_DWORD *)v8 + 22) = 7;
          sub_143028EE0(v8 + 13);
          v336 = sub_142C76FA0(v8, v8 + 12);
          return sub_142D72040(&off_1449B5288, v544, v336);
        }
LABEL_27:
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v544[0], 0);
        if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
          goto LABEL_461;
        v28 = v8[5];
        if ( *(_QWORD *)(v28 + 48) )
        {
          v29 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
          v30 = *(_UNKNOWN ***)(v28 + 40);
          if ( !v30 )
            v30 = &off_147097D08;
          v31 = sub_143028C10(&unk_144BDF900);
          sub_1408C22E0(v31, v30);
          v32 = sub_143028C10(&unk_144FE9240);
          v33 = *(_QWORD *)(v8[5] + 48);
          sub_142FBFE6C(v32);
          v544[0] = sub_1408B6310(v29, v31, v33, v32);
          if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
          {
            *((_DWORD *)v8 + 22) = 8;
            sub_143028EE0(v8 + 13);
            v34 = sub_142C76FA0(v8, v8 + 12);
            return sub_142D72040(&off_1449B5288, v544, v34);
          }
LABEL_19:
          if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
            sub_141DC8280(v544[0], 0);
        }
        if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
          goto LABEL_461;
        *(_QWORD *)(v8[5] + 64) = 0;
        v9 = sub_143028C10(&unk_144CBDA18);
        *(_QWORD *)(v9 + 104) = &off_146F76688;
        v10 = sub_143028C10(&unk_144D7C578);
        v11 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v11 + 8) = &off_14723C8B8;
        sub_143028E70(v10 + 8, v11);
        sub_143028E70(v9 + 80, v10);
        v12 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v12 + 40) = &off_146EEF8A0;
        *(_DWORD *)(v12 + 48) = 8;
        sub_141ADAE90(v9, &off_147109320, v12);
        v13 = sub_143028C10(&unk_144D7C1E0);
        v14 = sub_143028C10(&unk_144D7C578);
        v15 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v15 + 8) = &off_14723C8B8;
        sub_143028E70(v14 + 8, v15);
        sub_143028E70(v13 + 80, v14);
        v16 = *(_QWORD *)(v2 + 24);
        v17 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v17 + 40, v16);
        *(_DWORD *)(v17 + 48) = 8;
        sub_141ADAE90(v13, &off_147171D48, v17);
        v18 = v8[9];
        v19 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v19 + 40, v18);
        *(_DWORD *)(v19 + 48) = 8;
        sub_141ADAE90(v13, &off_14716D800, v19);
        v20 = sub_143028C10(&unk_144D7C1E0);
        v21 = sub_143028C10(&unk_144D7C578);
        v22 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v22 + 8) = &off_14723C8B8;
        sub_143028E70(v21 + 8, v22);
        sub_143028E70(v20 + 80, v21);
        v23 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v23 + 40) = &off_146DA8128;
        *(_DWORD *)(v23 + 48) = 8;
        sub_141ADAE90(v20, &off_147036118, v23);
        v24 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v24 + 40) = &off_146E355E8;
        *(_DWORD *)(v24 + 48) = 8;
        sub_141ADAE90(v20, &off_146FC05A8, v24);
        v25 = sub_141FD15C0(v8[7]);
        v26 = 0;
        if ( (unsigned int)sub_141FD2400(v25, &off_14709FB80, &v471, &v470) )
          v26 = v471;
        v471 = 0;
        if ( v26 )
        {
          v337 = sub_141DC0B60(v26, &off_144A7FC80);
          if ( (v337 & 2) != 0 )
            v27 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v337 - 2))(v26, *(_QWORD *)(v337 + 6));
          else
            v27 = ((__int64 (__fastcall *)(__int64))v337)(v26);
        }
        else
        {
          v27 = 0;
        }
        v338 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v338 + 40, v27);
        *(_DWORD *)(v338 + 48) = 8;
        sub_141ADAE90(v20, &off_146FD8F48, v338);
        v339 = sub_141FD15C0(v8[7]);
        v340 = 0;
        if ( (unsigned int)sub_141FD2400(v339, &off_147175AA8, &v469, &v468) )
          v340 = v469;
        v469 = 0;
        if ( v340 )
        {
          v341 = sub_141DC0B60(v340, &off_144A7FC80);
          if ( (v341 & 2) != 0 )
            v342 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v341 - 2))(v340, *(_QWORD *)(v341 + 6));
          else
            v342 = ((__int64 (__fastcall *)(__int64))v341)(v340);
        }
        else
        {
          v342 = 0;
        }
        v343 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v343 + 40, v342);
        *(_DWORD *)(v343 + 48) = 8;
        sub_141ADAE90(v20, &off_146FC0018, v343);
        v344 = sub_141FD15C0(v8[7]);
        v345 = 0;
        if ( (unsigned int)sub_141FD2400(v344, &off_146FC04B0, &v467, &v466) )
          v345 = v467;
        v467 = 0;
        if ( v345 )
        {
          v346 = sub_141DC0B60(v345, &off_144A7FC80);
          if ( (v346 & 2) != 0 )
            v347 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v346 - 2))(v345, *(_QWORD *)(v346 + 6));
          else
            v347 = ((__int64 (__fastcall *)(__int64))v346)(v345);
        }
        else
        {
          v347 = 0;
        }
        v348 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v348 + 40, v347);
        *(_DWORD *)(v348 + 48) = 8;
        sub_141ADAE90(v20, &off_146FC0628, v348);
        v349 = sub_141FD15C0(v8[7]);
        v350 = 0;
        if ( (unsigned int)sub_141FD2400(v349, &off_1470218F8, &v465, &v464) )
          v350 = v465;
        v465 = 0;
        if ( v350 )
        {
          v351 = sub_141DC0B60(v350, &off_144A7FC80);
          if ( (v351 & 2) != 0 )
            v352 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v351 - 2))(v350, *(_QWORD *)(v351 + 6));
          else
            v352 = ((__int64 (__fastcall *)(__int64))v351)(v350);
        }
        else
        {
          v352 = 0;
        }
        v353 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v353 + 40, v352);
        *(_DWORD *)(v353 + 48) = 8;
        sub_141ADAE90(v20, &off_147021820, v353);
        v354 = sub_141FD15C0(v8[7]);
        v355 = 0;
        if ( (unsigned int)sub_141FD2400(v354, &off_1470218C8, &v463, &v462) )
          v355 = v463;
        v463 = 0;
        if ( v355 )
        {
          v356 = sub_141DC0B60(v355, &off_144A7FC80);
          if ( (v356 & 2) != 0 )
            v357 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v356 - 2))(v355, *(_QWORD *)(v356 + 6));
          else
            v357 = ((__int64 (__fastcall *)(__int64))v356)(v355);
        }
        else
        {
          v357 = 0;
        }
        v358 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v358 + 40, v357);
        *(_DWORD *)(v358 + 48) = 8;
        sub_141ADAE90(v20, &off_1470217B0, v358);
        v359 = sub_141FD15C0(v8[6]);
        v360 = 0;
        if ( (unsigned int)sub_141FD2400(v359, &off_14714A4B8, &v461, &v460) )
          v360 = v461;
        v461 = 0;
        if ( v360 )
        {
          v361 = sub_141DC0B60(v360, &off_144A7FC80);
          if ( (v361 & 2) != 0 )
            v362 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v361 - 2))(v360, *(_QWORD *)(v361 + 6));
          else
            v362 = ((__int64 (__fastcall *)(__int64))v361)(v360);
        }
        else
        {
          v362 = 0;
        }
        v363 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v363 + 40, v362);
        *(_DWORD *)(v363 + 48) = 8;
        sub_141ADAE90(v20, &off_14716D588, v363);
        v364 = sub_141FD15C0(v8[7]);
        v365 = 0;
        if ( (unsigned int)sub_141FD2400(v364, &off_14701D188, &v459, &v458) )
          v365 = v459;
        v459 = 0;
        if ( v365 )
        {
          v366 = sub_141DC0B60(v365, &off_144A7FC80);
          if ( (v366 & 2) != 0 )
            v367 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v366 - 2))(v365, *(_QWORD *)(v366 + 6));
          else
            v367 = ((__int64 (__fastcall *)(__int64))v366)(v365);
        }
        else
        {
          v367 = 0;
        }
        v368 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v368 + 40, v367);
        *(_DWORD *)(v368 + 48) = 8;
        sub_141ADAE90(v20, &off_14701CFA8, v368);
        v369 = sub_141FD15C0(v8[6]);
        v370 = 0;
        if ( (unsigned int)sub_141FD2400(v369, &off_1471492E8, &v457, &v456) )
          v370 = v457;
        v457 = 0;
        if ( v370 )
        {
          v371 = sub_141DC0B60(v370, &off_144A7FC80);
          if ( (v371 & 2) != 0 )
            v372 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v371 - 2))(v370, *(_QWORD *)(v371 + 6));
          else
            v372 = ((__int64 (__fastcall *)(__int64))v371)(v370);
        }
        else
        {
          v372 = 0;
        }
        v373 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v373 + 40, v372);
        *(_DWORD *)(v373 + 48) = 8;
        sub_141ADAE90(v20, &off_14716D260, v373);
        v374 = sub_141FD15C0(v8[6]);
        v375 = 0;
        if ( (unsigned int)sub_141FD2400(v374, &off_147160DE0, &v455, &v454) )
          v375 = v455;
        v455 = 0;
        if ( v375 )
        {
          v376 = sub_141DC0B60(v375, &off_144A7FC80);
          if ( (v376 & 2) != 0 )
            v377 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v376 - 2))(v375, *(_QWORD *)(v376 + 6));
          else
            v377 = ((__int64 (__fastcall *)(__int64))v376)(v375);
        }
        else
        {
          v377 = 0;
        }
        v378 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v378 + 40, v377);
        *(_DWORD *)(v378 + 48) = 8;
        sub_141ADAE90(v20, &off_14716D2A8, v378);
        sub_141ADAE90(v13, &off_146F7C210, v20);
        v379 = v8[8];
        v380 = sub_143028C10(&unk_144D7C1E0);
        v381 = sub_143028C10(&unk_144D7C578);
        v382 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v382 + 8) = &off_14723C8B8;
        sub_143028E70(v381 + 8, v382);
        sub_143028E70(v380 + 80, v381);
        sub_141AD80A0(v380, v379, 0);
        sub_141ADAE90(v13, &off_146F71A38, v380);
        v383 = v8[10];
        v384 = sub_143028C10(&unk_144D7CCC0);
        sub_143028E70(v384 + 40, v383);
        *(_DWORD *)(v384 + 48) = 8;
        sub_141ADAE90(v13, &off_14710EA18, v384);
        v385 = sub_143028C10(&unk_144D7C1E0);
        v386 = sub_143028C10(&unk_144D7C578);
        v387 = sub_143028C10(&unk_145496718);
        *(_QWORD *)(v387 + 8) = &off_14723C8B8;
        sub_143028E70(v386 + 8, v387);
        sub_143028E70(v385 + 80, v386);
        v388 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v388 + 40) = &off_146D00F38;
        *(_DWORD *)(v388 + 48) = 8;
        sub_141ADAE90(v385, &off_147117308, v388);
        v389 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v389 + 40) = &off_146DA8128;
        *(_DWORD *)(v389 + 48) = 8;
        sub_141ADAE90(v385, &off_147117428, v389);
        sub_141ADAE90(v13, &off_147117368, v385);
        sub_141ADAE90(v9, &off_14717D2E8, v13);
        v390 = sub_143028C10(&unk_144D7CCC0);
        *(_QWORD *)(v390 + 40) = &off_1470E1FA0;
        *(_DWORD *)(v390 + 48) = 8;
        sub_141ADAE90(v9, &off_14711CCB0, v390);
        v391 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
        v392 = sub_143028C10(&unk_144BDF900);
        sub_1408C22E0(v392, &off_1470980E0);
        v393 = sub_143028C10(&unk_144FE9240);
        sub_142FBFE78(v393, v8[5]);
        v544[0] = sub_1408B6310(v391, v392, v9, v393);
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
        {
          *((_DWORD *)v545 + 22) = 9;
          sub_143028EE0(v545 + 13);
          v394 = sub_142C76FA0(v545, v545 + 12);
          return sub_142D72040(&off_1449B5288, v544, v394);
        }
LABEL_13:
        if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
          sub_141DC8280(v544[0], 0);
        if ( !(unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8)) )
          goto LABEL_461;
        v5 = v545;
        v6 = *(_QWORD *)(v545[5] + 64);
        if ( v6 )
        {
          v395 = sub_141FD15C0(v6);
          v7 = 0;
          if ( (unsigned int)sub_141FD2400(v395, &off_14716D6C8, &v453, &v452) )
            v7 = v453;
          v453 = 0;
        }
        else
        {
          v7 = 0;
        }
        if ( v7 )
        {
          v396 = sub_141DC0B60(v7, &off_144A7FC80);
          if ( (v396 & 2) != 0 )
            v397 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v396 - 2))(v7, *(_QWORD *)(v396 + 6));
          else
            v397 = ((__int64 (*)(void))v396)();
        }
        else
        {
          v397 = 0;
        }
        if ( (_UNKNOWN **)v397 != &off_146E76A38
          && (!v397
           || *(_DWORD *)(v397 + 8) != 7
           || *(_QWORD *)(v397 + 18) ^ 0x53005300450043LL | *(_QWORD *)(v397 + 12) ^ 0x43004300550053LL) )
        {
          v3 = *(_QWORD *)(v2 + 8);
          if ( *(_BYTE *)(v2 + 144) )
          {
            v244 = &off_146AEC898;
            goto LABEL_458;
          }
          v430 = *(_QWORD *)(v545[5] + 64);
          if ( v430 )
          {
            v431 = sub_141FD15C0(v430);
            v432 = 0;
            if ( (unsigned int)sub_141FD2400(v431, &off_14716D6C8, &v451, &v450) )
              v432 = v451;
            v451 = 0;
          }
          else
          {
            v432 = 0;
          }
          if ( v432 )
          {
            v433 = sub_141DC0B60(v432, &off_144A7FC80);
            if ( (v433 & 2) != 0 )
              v434 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v433 - 2))(v432, *(_QWORD *)(v433 + 6));
            else
              v434 = ((__int64 (*)(void))v433)();
            v4 = (_UNKNOWN **)v434;
          }
          else
          {
            v4 = nullptr;
          }
          if ( !v4 )
            v4 = &off_146F7C1E0;
          goto LABEL_457;
        }
        v398 = sub_141FD15C0(*(_QWORD *)(v545[5] + 64));
        v399 = 0;
        if ( (unsigned int)sub_141FD2400(v398, &off_14716D6F8, &v449, &v448) )
          v399 = v449;
        v449 = 0;
        if ( v399 )
        {
          v400 = sub_141DC0B60(v399, &off_144A7FC80);
          if ( (v400 & 2) != 0 )
            v401 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v400 - 2))(v399, *(_QWORD *)(v400 + 6));
          else
            v401 = ((__int64 (__fastcall *)(__int64))v400)(v399);
          v249 = v401;
        }
        else
        {
          v249 = 0;
        }
        v545[5] = 0;
        v545[9] = 0;
        v545[10] = 0;
        goto LABEL_425;
      }
      if ( !(unsigned int)sub_141CF4290(v243, &off_146E76A38) )
      {
        v3 = *(_QWORD *)(v2 + 8);
        if ( *(_BYTE *)(v2 + 144) )
        {
          v244 = &off_146AEC898;
LABEL_458:
          sub_140F9EFA0(v3, v244, &off_147149C08);
          goto LABEL_461;
        }
        v4 = (_UNKNOWN **)v243;
        if ( !v243 )
          v4 = &off_1470B9658;
        goto LABEL_457;
      }
      v245 = sub_141FD15C0(*(_QWORD *)(v545[3] + 56));
      v246 = 0;
      if ( (unsigned int)sub_141FD2400(v245, &off_147173188, &v447, &v446) )
        v246 = v447;
      v447 = 0;
      if ( v246 )
      {
        v247 = sub_141DC0B60(v246, &off_144A7FC80);
        if ( (v247 & 2) != 0 )
          v248 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v247 - 2))(v246, *(_QWORD *)(v247 + 6));
        else
          v248 = ((__int64 (__fastcall *)(__int64))v247)(v246);
      }
      else
      {
        v248 = 0;
      }
      v249 = v248;
      if ( !v248 )
      {
        v250 = sub_141FD15C0(v545[6]);
        v251 = 0;
        if ( (unsigned int)sub_141FD2400(v250, &off_14714A4B8, &v445, &v444) )
          v251 = v445;
        v445 = 0;
        if ( v251 )
        {
          v252 = sub_141DC0B60(v251, &off_144A7FC80);
          if ( (v252 & 2) != 0 )
            v253 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v252 - 2))(v251, *(_QWORD *)(v252 + 6));
          else
            v253 = ((__int64 (__fastcall *)(__int64))v252)(v251);
          v249 = v253;
        }
        else
        {
          v249 = 0;
        }
      }
LABEL_425:
      *(_QWORD *)(v5[3] + 64LL) = 0;
      v402 = sub_143028C10(&unk_144CBDA18);
      *(_QWORD *)(v402 + 104) = &off_146F76688;
      v403 = sub_143028C10(&unk_144D7C578);
      v404 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v404 + 8) = &off_14723C8B8;
      sub_143028E70(v403 + 8, v404);
      sub_143028E70(v402 + 80, v403);
      v405 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v405 + 40) = &off_146E6B8C0;
      *(_DWORD *)(v405 + 48) = 8;
      sub_141ADAE90(v402, &off_147109320, v405);
      v406 = sub_143028C10(&unk_144D7C1E0);
      v407 = sub_143028C10(&unk_144D7C578);
      v408 = sub_143028C10(&unk_145496718);
      *(_QWORD *)(v408 + 8) = &off_14723C8B8;
      sub_143028E70(v407 + 8, v408);
      sub_143028E70(v406 + 80, v407);
      v409 = *(_QWORD *)(v2 + 24);
      v410 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v410 + 40, v409);
      *(_DWORD *)(v410 + 48) = 8;
      sub_141ADAE90(v406, &off_147171D48, v410);
      v411 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v411 + 40) = &off_146E76A38;
      *(_DWORD *)(v411 + 48) = 8;
      sub_141ADAE90(v406, &off_147163478, v411);
      v412 = sub_141FD15C0(v5[6]);
      v413 = 0;
      if ( (unsigned int)sub_141FD2400(v412, &off_14714A4B8, &v443, &v442) )
        v413 = v443;
      v443 = 0;
      if ( v413 )
      {
        v414 = sub_141DC0B60(v413, &off_144A7FC80);
        if ( (v414 & 2) != 0 )
          v415 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v414 - 2))(v413, *(_QWORD *)(v414 + 6));
        else
          v415 = ((__int64 (__fastcall *)(__int64))v414)(v413);
      }
      else
      {
        v415 = 0;
      }
      v416 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v416 + 40, v415);
      *(_DWORD *)(v416 + 48) = 8;
      sub_141ADAE90(v406, &off_14714A4B8, v416);
      v417 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v417 + 40) = &off_146A622F8;
      *(_DWORD *)(v417 + 48) = 8;
      sub_141ADAE90(v406, &off_14703CA70, v417);
      v418 = sub_141FD15C0(v5[7]);
      v419 = 0;
      if ( (unsigned int)sub_141FD2400(v418, &off_14709FB80, &v441, &v440) )
        v419 = v441;
      v441 = 0;
      if ( v419 )
      {
        v420 = sub_141DC0B60(v419, &off_144A7FC80);
        if ( (v420 & 2) != 0 )
          v421 = (*(__int64 (__fastcall **)(__int64, _QWORD))(v420 - 2))(v419, *(_QWORD *)(v420 + 6));
        else
          v421 = ((__int64 (__fastcall *)(__int64))v420)(v419);
      }
      else
      {
        v421 = 0;
      }
      v422 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v422 + 40, v421);
      *(_DWORD *)(v422 + 48) = 8;
      sub_141ADAE90(v406, &off_146FD8F48, v422);
      v423 = sub_143028C10(&unk_144D7CCC0);
      sub_143028E70(v423 + 40, v249);
      *(_DWORD *)(v423 + 48) = 8;
      sub_141ADAE90(v406, &off_146F7BFC8, v423);
      v424 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v424 + 40) = &off_146EB4080;
      *(_DWORD *)(v424 + 48) = 8;
      sub_141ADAE90(v406, &off_1470A5D10, v424);
      sub_141ADAE90(v402, &off_14717D2E8, v406);
      v425 = sub_143028C10(&unk_144D7CCC0);
      *(_QWORD *)(v425 + 40) = &off_1470DC9B0;
      *(_DWORD *)(v425 + 48) = 8;
      sub_141ADAE90(v402, &off_14711CCB0, v425);
      v426 = *(_QWORD *)(*(_QWORD *)(v2 + 8) + 24LL);
      v427 = sub_143028C10(&unk_144BDF900);
      sub_1408C22E0(v427, &off_147098058);
      v428 = sub_143028C10(&unk_144FE9240);
      sub_142FBFD64(v428, v5[3]);
      v544[0] = sub_1408B6310(v426, v427, v402, v428);
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x1600000) == 0 )
      {
        *((_DWORD *)v545 + 22) = 10;
        sub_143028EE0(v545 + 13);
        v429 = sub_142C76FA0(v545, v545 + 12);
        return sub_142D72040(&off_1449B5288, v544, v429);
      }
LABEL_5:
      if ( (*(_DWORD *)(v544[0] + 52LL) & 0x11000000) != 0x1000000 )
        sub_141DC8280(v544[0], 0);
      if ( (unsigned int)sub_140F9E790(*(_QWORD *)(v2 + 8))
        && !(unsigned int)sub_141CF4290(*(_QWORD *)(v545[3] + 64), &off_146E30E40) )
      {
        v3 = *(_QWORD *)(v2 + 8);
        if ( *(_BYTE *)(v2 + 144) )
        {
          v244 = &off_146AEC898;
          goto LABEL_458;
        }
        v4 = *(_UNKNOWN ***)(v545[3] + 64);
        if ( !v4 )
          v4 = &off_14714CB50;
LABEL_457:
        v244 = (_UNKNOWN **)sub_141CF62D0(&off_146E3A0C8, v4, &off_146A951E8);
        goto LABEL_458;
      }
LABEL_461:
      *((_DWORD *)v545 + 22) = -2;
      v545[3] = 0;
      v545[6] = 0;
      v545[7] = 0;
      v545[8] = 0;
      v435 = v545 + 12;
      if ( v545[12] )
      {
        result = sub_14236B540(*v435, 0);
        if ( !(_DWORD)result )
        {
          __ExceptionPtrRethrow((const void *)0x18);
          __debugbreak();
        }
      }
      else
      {
        if ( *(&qword_147298A70 - 1) )
          sub_142F90006();
        return sub_143028EE0(v435);
      }
      return result;
  }
}
