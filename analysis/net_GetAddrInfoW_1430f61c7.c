/* caller of GetAddrInfoW @ 0x1430f61c7 */
// attributes: thunk
INT __stdcall GetAddrInfoW(PCWSTR pNodeName, PCWSTR pServiceName, const ADDRINFOW *pHints, PADDRINFOW *ppResult)
{
  return __imp_GetAddrInfoW(pNodeName, pServiceName, pHints, ppResult);
}
