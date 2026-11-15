/* x1 WSAConnect via cref @ 0x141cc25d0 */
__int64 __fastcall sub_141CC25D0(
        __int64 a1,
        const struct sockaddr **a2,
        int namelen,
        struct _WSABUF *lpCallerData,
        struct _WSABUF *lpCalleeData,
        struct _QualityOfService *lpSQOS,
        struct _QualityOfService *lpGQOS)
{
  SOCKET s; // r14
  unsigned int v11; // ebx
  WINERROR LastError; // esi
  _QWORD *ThreadLocalStoragePointer; // rcx
  __int64 v14; // rdi
  const struct sockaddr *name; // [rsp+44h] [rbp-94h]
  _BYTE v17[40]; // [rsp+58h] [rbp-80h] BYREF
  const struct sockaddr *name_1; // [rsp+80h] [rbp-58h]
  __int128 v19; // [rsp+88h] [rbp-50h] BYREF

  name_1 = nullptr;
  v19 = 0;
  *(_QWORD *)&v19 = a1;
  sub_141DC71A0(a1, (char *)&v19 + 8);
  name_1 = *a2;
  s = *(_QWORD *)(v19 + 8);
  SetLastError(0);
  name = name_1;
  sub_14301AE60(v17);
  v11 = WSAConnect(s, name, namelen, lpCallerData, lpCalleeData, lpSQOS, lpGQOS);
  sub_14301AEB0(v17);
  LastError = GetLastError();
  name_1 = nullptr;
  if ( BYTE8(v19) )
    sub_141DC7200(v19, 0);
  ThreadLocalStoragePointer = NtCurrentTeb()->ThreadLocalStoragePointer;
  v14 = *(_QWORD *)(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  if ( !v14 )
    v14 = sub_141DED040(ThreadLocalStoragePointer[TlsIndex] + 16LL);
  *(_DWORD *)(v14 + 424) = LastError;
  return v11;
}
