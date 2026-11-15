/* caller of WSAIoctl @ 0x1430f61eb */
// attributes: thunk
int __stdcall WSAIoctl(
        SOCKET s,
        DWORD dwIoControlCode,
        LPVOID lpvInBuffer,
        DWORD cbInBuffer,
        LPVOID lpvOutBuffer,
        DWORD cbOutBuffer,
        LPDWORD lpcbBytesReturned,
        LPWSAOVERLAPPED lpOverlapped,
        LPWSAOVERLAPPED_COMPLETION_ROUTINE lpCompletionRoutine)
{
  return __imp_WSAIoctl(
           s,
           dwIoControlCode,
           lpvInBuffer,
           cbInBuffer,
           lpvOutBuffer,
           cbOutBuffer,
           lpcbBytesReturned,
           lpOverlapped,
           lpCompletionRoutine);
}
