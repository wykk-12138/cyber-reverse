
/* ===== import NCryptCreatePersistedKey | NCryptCreatePersistedKey @ 0x1430f60e3 ===== */
// attributes: thunk
SECURITY_STATUS __stdcall NCryptCreatePersistedKey(
        NCRYPT_PROV_HANDLE hProvider,
        NCRYPT_KEY_HANDLE *phKey,
        LPCWSTR pszAlgId,
        LPCWSTR pszKeyName,
        DWORD dwLegacyKeySpec,
        DWORD dwFlags)
{
  return __imp_NCryptCreatePersistedKey(hProvider, phKey, pszAlgId, pszKeyName, dwLegacyKeySpec, dwFlags);
}
