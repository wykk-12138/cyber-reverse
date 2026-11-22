# C8 字符串池分类比对（生成物）

```
image strings: 213338   artifact strings: 117322

class               image  artifact exact-in-artifact
locale-key            971       935        19
url                  3507       283        14
error-message        4192       139        48
dependency           2277       692       218
other              202391    115273     25085

unknown (in the image, not found in the artifact — §4.5 says this means nothing yet):
  locale-key: 952 unknown; samples: Bogus.dllg | DSystem.Text.RegularExpressions.dll.Syst | System.Linq.dll2BouncyCastle.Cryptograph | MimeKit.dll8System.Security.Cryptography | DSystem.Diagnostics.TraceSource.dll.Syst | System.dll8System.Collections.Immutable
  url: 3493 unknown; samples: https://github.com/AzureAD/microsoft-aut | https://github.com/AzureAD/azure-actived | https://ipfs.io | http://www.typography.com/support/eula.h | http://ocsp.accv.es0 | http://www.cert.fnmt.es/dpcs/0\r
  error-message: 4144 unknown; samples: Newtonsoft.Json request bodies (LegacyJs | Live request stream from an application  | File system globbing to find files match | Logging infrastructure default implement | MediumHigh<Use SKSamplingOptions instea | BindingExpression and ReflectionBinding 

Limits, stated rather than papered over:
  1. the artifact side is a byte scan, and NativeAOT stores some literals in forms a scan cannot
     see, so "in the image, not in the artifact" is unknown, never missing (§4.5);
  2. the image pool carries referenced-assembly metadata — assembly names and NuGet
     descriptions — which no text rule separates perfectly, so these counts are upper bounds;
  3. the image side is IDA's own list, and it concatenates adjacent strings into one entry —
     samples like "Bogus.dllg" are two strings run together — which inflates the dotted classes;
  4. this answers "what is comparable", not "what matches": it is a comparison instrument,
     not a verdict on parity.
```
