/* caller of GetAddrInfoExW @ 0x1430f61c1 */
// attributes: thunk
INT __stdcall GetAddrInfoExW(
        PCWSTR pName,
        PCWSTR pServiceName,
        DWORD dwNameSpace,
        LPGUID lpNspId,
        const ADDRINFOEXW *hints,
        PADDRINFOEXW *ppResult,
        struct timeval *timeout,
        LPOVERLAPPED lpOverlapped,
        LPLOOKUPSERVICE_COMPLETION_ROUTINE lpCompletionRoutine,
        LPHANDLE lpHandle)
{
  return __imp_GetAddrInfoExW(
           pName,
           pServiceName,
           dwNameSpace,
           lpNspId,
           hints,
           ppResult,
           timeout,
           lpOverlapped,
           lpCompletionRoutine,
           lpHandle);
}
