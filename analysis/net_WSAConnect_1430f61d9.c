/* caller of WSAConnect @ 0x1430f61d9 */
// attributes: thunk
int __stdcall WSAConnect(
        SOCKET s,
        const struct sockaddr *name,
        int namelen,
        LPWSABUF lpCallerData,
        LPWSABUF lpCalleeData,
        LPQOS lpSQOS,
        LPQOS lpGQOS)
{
  return __imp_WSAConnect(s, name, namelen, lpCallerData, lpCalleeData, lpSQOS, lpGQOS);
}
