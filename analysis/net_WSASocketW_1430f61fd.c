/* caller of WSASocketW @ 0x1430f61fd */
// attributes: thunk
SOCKET __stdcall WSASocketW(int af, int type, int protocol, LPWSAPROTOCOL_INFOW lpProtocolInfo, GROUP g, DWORD dwFlags)
{
  return __imp_WSASocketW(af, type, protocol, lpProtocolInfo, g, dwFlags);
}
