# C8 字符串池分类比对（生成物）

```
image strings: 213338   artifact strings: 126238

class               image  artifact exact-in-artifact
locale-key           1003        24         0
url                  3451       286        15
error-message        4116       110        34
dependency           2502      2425       761
other              202266    123393     25879

unknown (in the image, not found in the artifact — §4.5 says this means nothing yet):
  locale-key: 1003 unknown; samples: Accounts.Action.Add | Accounts.Action.Clear | Accounts.Column.Added | Accounts.Column.Email | Accounts.Column.Password | Accounts.Context.CopyMany
  url: 3436 unknown; samples: https://ipfs.io | http://127.0.0.1: | http://169.254.169.254/metadata/instance | http://fail/ | http://localhost/ | http://localhost:
  error-message: 4082 unknown; samples: Y*#|Marshalling as Currency may be unava | Marshalling arbitrary types may be unava | Ke/fTasks will continue to run and use t | In-bot onlydRoute captchas exclusively t | Automatically assigns a random account t | Automatically assigns an account based o

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
