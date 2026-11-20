# 按类的状态机清单（由 `python analysis/async_tail.py --classes-doc` 生成）

> 状态机名 `<名字>d__NN` 在元数据里**按类成组**出现，`NN` 是该类内的方法序号。
> 所以相邻的一串名字就是**那个类的步骤清单**——这比一张扁平的名字表有用得多：
> 它让人能看出「这个类有十步，其中三步复刻件没有」。

三态含义同 `docs/ASYNC_TAIL.md`：`declared` 有同名方法 / `mentioned` 源码出现过但非声明 / `absent` 完全没有。

| 组 | 起始地址 | 步骤数 | 有同名 | 仅提及 | 缺 |
|---|---|---|---|---|---|
| 0 | `0x1431E380A` | 4 | 1 | 0 | 2 |
| 1 | `0x14320A9AB` | 4 | 2 | 0 | 0 |
| 2 | `0x14329B097` | 4 | 0 | 0 | 1 |
| 3 | `0x1432A39F1` | 5 | 3 | 0 | 2 |
| 4 | `0x1432A493F` | 26 | 3 | 0 | 5 |
| 5 | `0x1432B4C03` | 6 | 0 | 0 | 2 |
| 6 | `0x1432CE017` | 4 | 2 | 0 | 1 |
| 7 | `0x1432CF382` | 21 | 3 | 0 | 5 |
| 8 | `0x1432D0397` | 18 | 1 | 0 | 9 |
| 9 | `0x1432D9A11` | 5 | 1 | 0 | 2 |
| 10 | `0x1432DD0D3` | 4 | 0 | 0 | 2 |
| 11 | `0x1432DF7D5` | 3 | 1 | 0 | 1 |
| 12 | `0x1432E245B` | 4 | 2 | 0 | 2 |
| 13 | `0x1432E5A93` | 3 | 0 | 0 | 2 |
| 14 | `0x1432E9519` | 9 | 1 | 0 | 4 |
| 15 | `0x1432EBC51` | 7 | 1 | 0 | 1 |
| 16 | `0x1432F0F66` | 13 | 1 | 1 | 7 |
| 17 | `0x1432F929E` | 15 | 1 | 1 | 3 |
| 18 | `0x143301627` | 10 | 5 | 0 | 4 |
| 19 | `0x143305458` | 3 | 1 | 1 | 1 |
| 20 | `0x14330632F` | 14 | 5 | 1 | 4 |
| 21 | `0x1433101AA` | 5 | 4 | 0 | 1 |
| 22 | `0x143310DE7` | 6 | 4 | 0 | 2 |
| 23 | `0x14331B7E3` | 20 | 9 | 2 | 4 |
| 24 | `0x14331DE94` | 17 | 3 | 1 | 11 |
| 25 | `0x14332B3AE` | 11 | 3 | 1 | 3 |
| 26 | `0x14332DEFB` | 4 | 3 | 0 | 1 |
| 27 | `0x1433661F7` | 24 | 10 | 0 | 1 |
| 28 | `0x143367677` | 58 | 22 | 2 | 14 |
| 29 | `0x14336AB45` | 28 | 15 | 3 | 6 |
| 30 | `0x14336D6A1` | 12 | 5 | 1 | 3 |
| 31 | `0x14336EA03` | 15 | 12 | 0 | 0 |
| 32 | `0x14336F848` | 29 | 11 | 0 | 0 |
| 33 | `0x143370E4A` | 33 | 17 | 1 | 3 |
| 34 | `0x143372AEA` | 64 | 27 | 4 | 9 |
| 35 | `0x1433779BB` | 21 | 5 | 0 | 10 |
| 36 | `0x14337998D` | 36 | 23 | 2 | 1 |
| 37 | `0x14337BDA2` | 90 | 17 | 8 | 9 |
| 38 | `0x143380569` | 44 | 22 | 3 | 3 |
| 39 | `0x14338251D` | 17 | 5 | 2 | 1 |
| 40 | `0x143383281` | 38 | 14 | 2 | 10 |
| 41 | `0x143385F1B` | 27 | 12 | 1 | 1 |
| 42 | `0x143387385` | 22 | 14 | 0 | 0 |
| 43 | `0x143388674` | 11 | 8 | 0 | 0 |
| 44 | `0x143389082` | 20 | 17 | 0 | 0 |
| 45 | `0x143389DBB` | 26 | 12 | 0 | 1 |
| 46 | `0x14338B004` | 23 | 9 | 0 | 0 |
| 47 | `0x14338C233` | 13 | 10 | 0 | 1 |
| 48 | `0x14338CC84` | 26 | 14 | 0 | 4 |
| 49 | `0x14338E2D6` | 23 | 10 | 0 | 3 |
| 50 | `0x14338F68C` | 22 | 5 | 1 | 2 |
| 51 | `0x1433909BC` | 23 | 16 | 0 | 0 |
| 52 | `0x143391B79` | 11 | 7 | 0 | 0 |
| 53 | `0x143392611` | 12 | 6 | 0 | 1 |
| 54 | `0x14339309B` | 28 | 9 | 0 | 2 |
| 55 | `0x14339461C` | 47 | 22 | 0 | 5 |
| 56 | `0x1433973D0` | 98 | 29 | 1 | 11 |
| 57 | `0x14339D6DF` | 24 | 10 | 3 | 4 |
| 58 | `0x14339FBFD` | 9 | 5 | 0 | 1 |
| 59 | `0x1433A0F23` | 22 | 7 | 4 | 2 |
| 60 | `0x1433A29C0` | 3 | 0 | 0 | 1 |
| 61 | `0x1433A31E2` | 18 | 8 | 0 | 0 |
| 62 | `0x1433A46E9` | 25 | 8 | 4 | 0 |
| 63 | `0x1433A6190` | 12 | 8 | 0 | 3 |
| 64 | `0x1433AD7FE` | 8 | 2 | 0 | 3 |
| 65 | `0x1433C0B32` | 10 | 6 | 2 | 2 |
| 66 | `0x1433C8193` | 7 | 5 | 0 | 0 |
| 67 | `0x1433CE24E` | 7 | 2 | 1 | 0 |
| 68 | `0x1433D1180` | 5 | 0 | 0 | 2 |
| 69 | `0x1433D4B67` | 5 | 4 | 0 | 0 |
| 70 | `0x1433D62D2` | 8 | 4 | 1 | 2 |
| 71 | `0x1433D8E3A` | 3 | 0 | 0 | 3 |
| 72 | `0x1433E2F4E` | 68 | 3 | 0 | 2 |
| 73 | `0x1433E64DB` | 7 | 1 | 0 | 2 |
| 74 | `0x1433E7A69` | 3 | 0 | 1 | 1 |
| 75 | `0x14341A518` | 9 | 1 | 0 | 2 |
| 76 | `0x14341C3F7` | 63 | 7 | 1 | 16 |
| 77 | `0x14341F09E` | 5 | 1 | 1 | 2 |
| 78 | `0x14343377F` | 4 | 1 | 0 | 2 |
| 79 | `0x14343C814` | 8 | 1 | 2 | 2 |
| 80 | `0x143447729` | 16 | 7 | 2 | 3 |
| 81 | `0x143449937` | 8 | 2 | 0 | 3 |
| 82 | `0x14344A208` | 39 | 8 | 6 | 13 |
| 83 | `0x14344DF3F` | 6 | 4 | 1 | 1 |
| 84 | `0x14344E9C9` | 3 | 1 | 1 | 0 |
| 85 | `0x143452BC5` | 8 | 3 | 0 | 4 |
| 86 | `0x1434543FE` | 28 | 6 | 1 | 12 |
| 87 | `0x14345A632` | 43 | 8 | 5 | 10 |
| 88 | `0x14345D905` | 41 | 18 | 2 | 14 |
| 89 | `0x14348BE65` | 10 | 1 | 0 | 6 |
| 90 | `0x1434A6A7D` | 11 | 5 | 2 | 2 |
| 91 | `0x1434A9595` | 39 | 15 | 0 | 3 |
| 92 | `0x1434AB921` | 26 | 12 | 2 | 0 |
| 93 | `0x1434ACEF3` | 15 | 5 | 1 | 0 |
| 94 | `0x1434AD998` | 29 | 14 | 1 | 6 |
| 95 | `0x1434AF56E` | 21 | 11 | 0 | 3 |
| 96 | `0x1434B0CC2` | 17 | 12 | 0 | 0 |
| 97 | `0x1434B1B15` | 26 | 17 | 0 | 0 |
| 98 | `0x1434B2F7C` | 23 | 17 | 0 | 0 |
| 99 | `0x1434B407E` | 7 | 5 | 0 | 2 |
| 100 | `0x1434B544A` | 13 | 7 | 0 | 0 |
| 101 | `0x1434B9F00` | 5 | 2 | 0 | 1 |
| 102 | `0x1434BCDD5` | 80 | 14 | 0 | 11 |
| 103 | `0x1434BFFE6` | 8 | 1 | 0 | 3 |
| 104 | `0x1434C2E07` | 86 | 13 | 0 | 4 |
| 105 | `0x1434C59BE` | 31 | 6 | 1 | 8 |
| 106 | `0x1434CD41F` | 5 | 1 | 1 | 3 |
| 107 | `0x1434CEA4D` | 23 | 2 | 0 | 3 |
| 108 | `0x1434D0DFF` | 5 | 2 | 1 | 0 |
| 109 | `0x14350E184` | 7 | 0 | 1 | 5 |
| 110 | `0x14350F341` | 4 | 0 | 1 | 3 |
| 111 | `0x1435104C5` | 14 | 0 | 0 | 9 |
| 112 | `0x143512495` | 23 | 2 | 0 | 5 |
| 113 | `0x14351D642` | 5 | 0 | 0 | 1 |
| 114 | `0x14351DEA8` | 13 | 3 | 1 | 6 |
| 115 | `0x143521146` | 13 | 1 | 0 | 8 |
| 116 | `0x143525B34` | 4 | 1 | 1 | 2 |
| 117 | `0x14353A8C2` | 28 | 4 | 0 | 5 |
| 118 | `0x14353BDF0` | 10 | 2 | 3 | 2 |
| 119 | `0x14353D2CD` | 5 | 1 | 0 | 1 |
| 120 | `0x14353EF23` | 10 | 0 | 0 | 1 |
| 121 | `0x14354062E` | 24 | 0 | 1 | 10 |
| 122 | `0x14354B0A6` | 3 | 0 | 0 | 2 |
| 123 | `0x1435B3679` | 17 | 4 | 0 | 7 |
| 124 | `0x1435B91C4` | 12 | 2 | 1 | 5 |
| 125 | `0x1435BACCB` | 4 | 2 | 0 | 0 |
| 126 | `0x1435BBD12` | 13 | 1 | 0 | 9 |
| 127 | `0x1435BE9D0` | 6 | 1 | 1 | 4 |
| 128 | `0x1435C33D8` | 8 | 2 | 0 | 3 |
| 129 | `0x1435C694B` | 27 | 3 | 0 | 9 |
| 130 | `0x1435C80AA` | 8 | 3 | 0 | 0 |
| 131 | `0x1435E8752` | 3 | 2 | 0 | 1 |
| 132 | `0x1435E9B02` | 3 | 0 | 0 | 2 |
| 133 | `0x1435EDE5F` | 22 | 6 | 0 | 2 |
| 134 | `0x1435F7F2D` | 6 | 1 | 0 | 4 |
| 135 | `0x1435F8CFB` | 18 | 1 | 0 | 11 |
| 136 | `0x1435FC1CA` | 4 | 1 | 0 | 2 |

## 组 0 · `0x1431E380A`

| d__ | 名字 | 状态 |
|---|---|---|
| 50 | `InitAsync` | declared |
| 51 | `InitAsync` | declared |
| 59 | `ConnectionLoop` | **absent** |
| 66 | `ValidateInput` | **absent** |

## 组 2 · `0x14329B097`

| d__ | 名字 | 状态 |
|---|---|---|
| 27 | `OverrideAsyncMethod` | **absent** |
| 7 | `OverrideAsyncMethod` | **absent** |
| 1 | `OverrideAsyncMethod` | **absent** |
| 10 | `OverrideAsyncMethod` | **absent** |

## 组 3 · `0x1432A39F1`

| d__ | 名字 | 状态 |
|---|---|---|
| 73 | `ConnectNetworkAsync` | **absent** |
| 31 | `ReadAsync` | declared |
| 34 | `WriteAsync` | declared |
| 40 | `EnumerateSerializedSubsets` | **absent** |
| 36 | `GetEnumerator` | declared |

## 组 4 · `0x1432A493F`

| d__ | 名字 | 状态 |
|---|---|---|
| 136 | `MergeHeaders` | **absent** |
| 1124 | `WriteToAsync` | declared |
| 5 | `get_Mailboxes` | **absent** |
| 88 | `ConstructMessagePartAsync` | **absent** |
| 7 | `ConstructMimePartAsync` | **absent** |
| 12 | `ConstructMultipartAsync` | **absent** |
| 141 | `GetEnumerator` | declared |
| 10 | `MultipartScanEpilogueAsync` | **absent** |
| 9 | `MultipartScanPreambleAsync` | **absent** |
| 110 | `MultipartScanSubpartsAsync` | **absent** |
| 130 | `ParseHeadersAsync` | **absent** |
| 15 | `ParseMessageAsync` | **absent** |
| 0 | `ReadAheadAsync` | **absent** |
| 6 | `ScanContentAsync` | **absent** |
| 4 | `SkipLineAsync` | **absent** |
| 58 | `StepAsync` | declared |
| 1 | `StepByteOrderMarkAsync` | **absent** |
| 32 | `StepHeadersAsync` | **absent** |
| 2 | `StepMboxMarkerAsync` | **absent** |
| 60 | `TokenizeText` | **absent** |
| 38 | `WriteToAsync` | declared |
| 20 | `DecodeToAsync` | **absent** |
| 13 | `WriteToAsync` | declared |
| 18 | `WriteToAsync` | declared |
| 402 | `WriteToAsync` | declared |
| 41 | `WriteToAsync` | declared |

## 组 5 · `0x1432B4C03`

| d__ | 名字 | 状态 |
|---|---|---|
| 496 | `AcquireUpdateLock` | **absent** |
| 38 | `CheckForUpdatesAsync` | **absent** |
| 456 | `DownloadAndApplyDeltaUpdates` | **absent** |
| 41 | `DownloadUpdatesAsync` | **absent** |
| 47 | `VerifyPackageChecksumAsync` | **absent** |
| 39 | `FromZipPackageGenerateChecksumAsync` | **absent** |

## 组 6 · `0x1432CE017`

| d__ | 名字 | 状态 |
|---|---|---|
| 5 | `GetEnumerator` | declared |
| 33 | `WaitUntilCountOrTimeoutAsync` | **absent** |
| 7 | `InvokeAsync` | declared |
| 8 | `InvokeAsync` | declared |

## 组 7 · `0x1432CF382`

| d__ | 名字 | 状态 |
|---|---|---|
| 616 | `FinishWriteAsync` | **absent** |
| 48 | `ReadAtLeastAsyncCore` | **absent** |
| 57 | `DisposeAsync` | declared |
| 68 | `CopyToAsyncCore` | **absent** |
| 332 | `DisposeAsync` | declared |
| 372 | `DisposeAsyncCore` | declared |
| 36 | `FlushAsyncInternal` | **absent** |
| 40 | `FlushWriteAsync` | **absent** |
| 48 | `ReadFromUnderlyingStreamAsync` | **absent** |
| 71 | `WriteAsyncInternal` | **absent** |
| 672 | `WriteAsyncInternal` | **absent** |
| 59 | `WriteToUnderlyingStreamAsync` | **absent** |
| 100 | `InternalReadAllBytesAsync` | **absent** |
| 101 | `InternalReadAllBytesUnknownLengthAsync` | **absent** |
| 106 | `InternalReadAllLinesAsync` | **absent** |
| 94 | `InternalReadAllTextAsync` | **absent** |
| 69 | `ReadAsyncInternal` | **absent** |
| 728 | `ReadBufferAsync` | **absent** |
| 63 | `ReadLineAsyncInternal` | **absent** |
| 66 | `ReadToEndAsyncInternal` | **absent** |
| 174 | `ReadToEndAsync` | declared |

## 组 8 · `0x1432D0397`

| d__ | 名字 | 状态 |
|---|---|---|
| 1 | `Select` | declared |
| 420 | `LocationChanged` | **absent** |
| 404 | `FinishLoadingAsync` | **absent** |
| 401 | `GetAttachedReferences` | **absent** |
| 7 | `LoadTextAsync` | **absent** |
| 12 | `WaitForReadyAsync` | **absent** |
| 6 | `GetDescendendElements` | **absent** |
| 17 | `GetOptions` | **absent** |
| 11 | `GetAncestors` | **absent** |
| 8 | `GetDescendantsAndSelf` | **absent** |
| 12 | `GetInclusiveAncestors` | **absent** |
| 49 | `EnsureAvailableAsync` | **absent** |
| 51 | `InitializeAsync` | **absent** |
| 53 | `ReadPreludeAsync` | **absent** |
| 370 | `DetectByteOrderMarkAsync` | **absent** |
| 38 | `ExpandBufferAsync` | **absent** |
| 334 | `PrefetchAllAsync` | **absent** |
| 39 | `ReadIntoBufferAsync` | **absent** |

## 组 9 · `0x1432D9A11`

| d__ | 名字 | 状态 |
|---|---|---|
| 23 | `Start` | declared |
| 0 | `GetLogicalAncestors` | **absent** |
| 4 | `GetLogicalDescendants` | **absent** |
| 1 | `GetSelfAndLogicalAncestors` | **absent** |
| 5 | `GetSelfAndLogicalDescendants` | **absent** |

## 组 10 · `0x1432DD0D3`

| d__ | 名字 | 状态 |
|---|---|---|
| 8 | `GetSelfAndVisualAncestors` | **absent** |
| 160 | `GetSelfAndVisualDescendants` | **absent** |
| 36 | `GetVisualAncestors` | **absent** |
| 15 | `GetVisualDescendants` | **absent** |

## 组 11 · `0x1432DF7D5`

| d__ | 名字 | 状态 |
|---|---|---|
| 3 | `GetItems` | **absent** |
| 1 | `TryGetValueAsync` | declared |
| 1 | `GetItems` | **absent** |

## 组 12 · `0x1432E245B`

| d__ | 名字 | 状态 |
|---|---|---|
| 1064 | `PopulateAsync` | **absent** |
| 234 | `Copy` | declared |
| 233 | `Cut` | **absent** |
| 235 | `Paste` | declared |

## 组 13 · `0x1432E5A93`

| d__ | 名字 | 状态 |
|---|---|---|
| 141 | `AnimateViewportOffsetAsync` | **absent** |
| 1434 | `RunCompletionAnimation` | **absent** |
| 129 | `RunTransitionAsync` | **absent** |

## 组 14 · `0x1432E9519`

| d__ | 名字 | 状态 |
|---|---|---|
| 616 | `CopyToClipboard` | **absent** |
| 722 | `GetAllRows` | **absent** |
| 59 | `GetDisplayedColumns` | **absent** |
| 60 | `GetDisplayedColumns` | **absent** |
| 62 | `GetDisplayedColumnsReverse` | **absent** |
| 45 | `GetScrollingElements` | **absent** |
| 26 | `GetEnumerator` | declared |
| 22 | `GetIndexes` | **absent** |
| 23 | `GetIndexes` | **absent** |

## 组 15 · `0x1432EBC51`

| d__ | 名字 | 状态 |
|---|---|---|
| 60 | `ClearAsync` | declared |
| 5 | `OpenClipboardAsync` | **absent** |
| 8 | `SetDataAsync` | **absent** |
| 9 | `TryGetDataAsync` | **absent** |
| 118 | `OpenFilePickerWithResultAsync` | **absent** |
| 10 | `OpenFolderPickerAsync` | **absent** |
| 12 | `SaveFilePickerWithResultAsync` | **absent** |

## 组 16 · `0x1432F0F66`

| d__ | 名字 | 状态 |
|---|---|---|
| 56 | `Enumerate` | mentioned |
| 30 | `GetEnumerator` | declared |
| 16 | `AsEnumerable` | **absent** |
| 16 | `GetEnumerator` | declared |
| 8 | `Sequence` | **absent** |
| 3 | `FindAll` | **absent** |
| 49 | `Enumerate` | mentioned |
| 57 | `GetEnumerator` | declared |
| 24 | `OnPaste` | **absent** |
| 22 | `StartDrag` | **absent** |
| 21 | `GetRectsForSegmentImpl` | **absent** |
| 23 | `ProcessTextLines` | **absent** |
| 46 | `get_AllNodes` | **absent** |

## 组 17 · `0x1432F929E`

| d__ | 名字 | 状态 |
|---|---|---|
| 51 | `GetExpandoEnumerator` | **absent** |
| 39 | `ArrayChunkIterator` | **absent** |
| 36 | `CastIterator` | mentioned |
| 40 | `EnumerableChunkIterator` | **absent** |
| 88 | `ExceptIterator` | **absent** |
| 121 | `IntersectIterator` | **absent** |
| 251 | `SelectIterator` | **absent** |
| 262 | `SelectManyIterator` | **absent** |
| 266 | `SelectManyIterator` | **absent** |
| 281 | `SkipWhileIterator` | **absent** |
| 316 | `TakeRangeFromEndIterator` | **absent** |
| 318 | `TakeWhileIterator` | **absent** |
| 350 | `WhereIterator` | **absent** |
| 362 | `ZipIterator` | **absent** |
| 13 | `GetEnumerator` | declared |

## 组 18 · `0x143301627`

| d__ | 名字 | 状态 |
|---|---|---|
| 84 | `StartAsync` | declared |
| 96 | `Monitor` | declared |
| 72 | `SetupProxySession` | **absent** |
| 77 | `StartBase` | **absent** |
| 87 | `GetCaptcha` | declared |
| 89 | `GetCaptcha` | declared |
| 100 | `Delay` | declared |
| 102 | `ScheduleWait` | **absent** |
| 105 | `GetMonitorDelay` | **absent** |
| 106 | `Login` | declared |

## 组 19 · `0x143305458`

| d__ | 名字 | 状态 |
|---|---|---|
| 24 | `GetRandom` | **absent** |
| 54 | `Invalidate` | mentioned |
| 55 | `GetAuthToken` | declared |

## 组 20 · `0x14330632F`

| d__ | 名字 | 状态 |
|---|---|---|
| 83 | `SetupProfile` | **absent** |
| 84 | `ResetIdentity` | **absent** |
| 86 | `Load` | declared |
| 87 | `Remove` | declared |
| 88 | `Load` | declared |
| 97 | `DisposeAsync` | declared |
| 90 | `OnAccountChanged` | **absent** |
| 89 | `OnFilterChanged` | **absent** |
| 114 | `RequestCompleted` | **absent** |
| 1150 | `Recaptcha` | declared |
| 116 | `Recaptcha_Source` | **absent** |
| 1170 | `Turnstile` | mentioned |
| 118 | `Turnstile_Source` | **absent** |
| 120 | `Click` | declared |

## 组 21 · `0x1433101AA`

| d__ | 名字 | 状态 |
|---|---|---|
| 20 | `StopAsync` | declared |
| 30 | `DispatchLoop` | **absent** |
| 31 | `FlushOnceAsync` | declared |
| 33 | `DrainLocalQueueAsync` | declared |
| 35 | `SendAsync` | declared |

## 组 22 · `0x143310DE7`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `GetOrAddAsync` | declared |
| 10 | `GetScript` | declared |
| 11 | `GenerateSensor` | declared |
| 12 | `SubmitSensor` | declared |
| 10 | `CreateProfile` | **absent** |
| 12 | `GetFingerprint` | **absent** |

## 组 23 · `0x14331B7E3`

| d__ | 名字 | 状态 |
|---|---|---|
| 8 | `Solve` | declared |
| 34 | `GetSensorData` | declared |
| 35 | `Generate` | declared |
| 36 | `GetSbsdData` | declared |
| 37 | `GetSbsdScript` | **absent** |
| 38 | `GenerateSbsd` | declared |
| 39 | `SolveCptChallenge` | declared |
| 30 | `GetSensorData` | declared |
| 31 | `Generate` | declared |
| 32 | `GetSbsdData` | declared |
| 33 | `GetSbsdHash` | **absent** |
| 34 | `GenerateSbsd` | declared |
| 35 | `SolveCptChallenge` | declared |
| 0 | `EvaluateAsync` | declared |
| 3 | `LoadAsync` | declared |
| 15 | `Dequeue` | mentioned |
| 27 | `TakeUntil` | **absent** |
| 70 | `DownloadAsync` | mentioned |
| 71 | `CopyToAsync` | declared |
| 42 | `GetFlags` | **absent** |

## 组 24 · `0x14331DE94`

| d__ | 名字 | 状态 |
|---|---|---|
| 5 | `GenerateAsync` | declared |
| 10 | `ShortenUrl` | **absent** |
| 18 | `LaunchBrowserLimit` | **absent** |
| 23 | `Process` | declared |
| 24 | `ProcessGuest` | **absent** |
| 26 | `LoadCheckoutPage` | **absent** |
| 25 | `LoadGuestSignup` | **absent** |
| 28 | `SubmitCheckoutPayment` | **absent** |
| 33 | `WalkObjects` | **absent** |
| 34 | `GetPayPalPaymentOptions` | **absent** |
| 35 | `SetCurrency` | **absent** |
| 36 | `ApproveMemberPayment` | **absent** |
| 37 | `GetThreeDsJwtQuery` | declared |
| 38 | `SolvePayPal3DS` | mentioned |
| 39 | `SolvePayPalHosted3DS` | **absent** |
| 416 | `ApproveOnBoard` | **absent** |
| 40 | `OnBoardGuest` | **absent** |

## 组 25 · `0x14332B3AE`

| d__ | 名字 | 状态 |
|---|---|---|
| 0 | `Solve3DS` | declared |
| 1 | `Solve3DSToken` | mentioned |
| 2 | `Solve3DSRedirect` | declared |
| 3 | `Process` | declared |
| 4 | `Process` | declared |
| 4 | `ProcessPoll` | **absent** |
| 5 | `ProcessRisk` | **absent** |
| 2 | `Process` | declared |
| 3 | `Poll3D` | **absent** |
| 17 | `Process` | declared |
| 5 | `Process` | declared |

## 组 26 · `0x14332DEFB`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `HandleResponse` | declared |
| 7 | `GetInputs` | **absent** |
| 8 | `SubmitSensor` | declared |
| 9 | `GenerateSensor` | declared |

## 组 27 · `0x1433661F7`

| d__ | 名字 | 状态 |
|---|---|---|
| 29 | `SendAsync` | declared |
| 59 | `AddAsync` | declared |
| 62 | `ExecuteAsync` | declared |
| 11 | `SolveAsync` | declared |
| 16 | `FetchBalance` | declared |
| 12 | `PollAsync` | declared |
| 13 | `PollCaptchaAsync` | **absent** |
| 8 | `SolveAsync` | declared |
| 9 | `PollAsync` | declared |
| 12 | `FetchBalance` | declared |
| 9 | `StartAsync` | declared |
| 11 | `InitializeAsync` | **absent** |
| 10 | `StopAsync` | declared |
| 9 | `SolveAsync` | declared |
| 14 | `FetchBalance` | declared |
| 10 | `PollAsync` | declared |
| 11 | `PollCaptchaAsync` | **absent** |
| 10 | `SolveAsync` | declared |
| 36 | `StartAsync` | declared |
| 37 | `StopAsync` | declared |
| 38 | `LoadAsync` | declared |
| 39 | `WriteAsync` | declared |
| 42 | `WriteToFileAsync` | **absent** |
| 43 | `ExecuteAsync` | declared |

## 组 28 · `0x143367677`

| d__ | 名字 | 状态 |
|---|---|---|
| 5 | `StartAsync` | declared |
| 6 | `StopAsync` | declared |
| 48 | `StartAsync` | declared |
| 54 | `ConnectAsync` | declared |
| 49 | `StartAsync` | declared |
| 50 | `StopAsync` | declared |
| 55 | `DisconnectAsync` | declared |
| 56 | `GetMessagesAsync` | **absent** |
| 57 | `ExecuteAsync` | declared |
| 59 | `GetPublicClientOAuth2CredentialsAsync` | **absent** |
| 60 | `FindAccountAsync` | **absent** |
| 7 | `SignInWithBrowserAsync` | **absent** |
| 8 | `SignInWithCodeAsync` | **absent** |
| 10 | `AcceptCallbacksAsync` | **absent** |
| 11 | `ReadCallbackAsync` | **absent** |
| 12 | `RespondAsync` | **absent** |
| 13 | `PostAsync` | declared |
| 18 | `AuthenticateAsync` | declared |
| 162 | `LogoutAsync` | **absent** |
| 170 | `LogoutAsync_Source` | **absent** |
| 20 | `GetConfig` | **absent** |
| 19 | `StopAsync` | declared |
| 23 | `ActivateAsync` | **absent** |
| 21 | `GetShared` | **absent** |
| 27 | `ExecuteAsync` | declared |
| 252 | `ResetAsync` | declared |
| 26 | `VerifyLicenseAsync` | **absent** |
| 15 | `Reconnected` | **absent** |
| 17 | `StartAsync` | declared |
| 19 | `SendAsync` | declared |
| 18 | `StopAsync` | declared |
| 23 | `SendGroupAsync` | mentioned |
| 24 | `InvokeAsync` | declared |
| 8 | `StartAsync` | declared |
| 10 | `RefreshTokenAsync` | **absent** |
| 8 | `FlushAsync` | declared |
| 11 | `StopAsync` | declared |
| 20 | `WaitAsync` | declared |
| 21 | `VerifyAsync` | declared |
| 22 | `CreateAsync` | declared |
| 37 | `PollAsync` | declared |
| 38 | `FetchAsync` | mentioned |
| 5 | `BackupAsync` | declared |
| 6 | `RestoreAsync` | declared |
| 11 | `ExecuteAsync` | declared |
| 4 | `ExecuteAsync` | declared |
| 12 | `AddProviderAsync` | declared |
| 13 | `RemoveProviderAsync` | **absent** |
| 14 | `AddAsync` | declared |
| 16 | `RemoteSolve` | **absent** |
| 15 | `RemoveAsync` | declared |
| 18 | `LoadAsync` | declared |
| 19 | `LoadAsync` | declared |
| 20 | `LoadAsync` | declared |
| 21 | `StartAsync` | declared |
| 22 | `StopAsync` | declared |
| 4 | `GetAnalyticsAsync` | **absent** |
| 5 | `ListAsync` | declared |

## 组 29 · `0x14336AB45`

| d__ | 名字 | 状态 |
|---|---|---|
| 0 | `GetAsync` | declared |
| 2 | `GetAsync` | declared |
| 13 | `StartAsync` | declared |
| 14 | `InstallAsync` | mentioned |
| 15 | `DownloadAsync` | mentioned |
| 16 | `DownloadPackageAsync` | **absent** |
| 18 | `AcquireLockAsync` | **absent** |
| 7 | `RunAsync` | declared |
| 8 | `ConnectAsync` | declared |
| 10 | `SessionAsync` | mentioned |
| 15 | `WriteRawFrameAsync` | **absent** |
| 16 | `ReadFrameAsync` | declared |
| 3 | `CheckAsync` | declared |
| 5 | `WaitAsync` | declared |
| 6 | `AddProviderAsync` | declared |
| 7 | `RemoveProviderAsync` | **absent** |
| 9 | `StopAsync` | declared |
| 7 | `ExecuteAsync` | declared |
| 8 | `WriteAsync` | declared |
| 12 | `ExecuteAsync` | declared |
| 0 | `WaitAsync` | declared |
| 1 | `Guard` | declared |
| 2 | `WaitImapAsync` | declared |
| 22 | `SetCachedProductAsync` | **absent** |
| 1 | `ExecuteAsync` | declared |
| 2 | `RefreshAsync` | declared |
| 3 | `GenTokenAsync` | **absent** |
| 4 | `ListAsync` | declared |

## 组 30 · `0x14336D6A1`

| d__ | 名字 | 状态 |
|---|---|---|
| 16 | `ChannelChangedAsync` | **absent** |
| 26 | `FindAsync` | **absent** |
| 18 | `ForceUpdateAsync` | **absent** |
| 17 | `UpdateAsync` | declared |
| 27 | `CheckForceAsync` | **absent** |
| 29 | `AnnounceAsync` | **absent** |
| 28 | `CheckAsync` | declared |
| 30 | `DownloadAsync` | mentioned |
| 45 | `StartAsync` | declared |
| 1 | `DownloadImageAsync` | **absent** |
| 13 | `PostAsync` | declared |
| 3 | `SendAsync` | declared |

## 组 33 · `0x143370E4A`

| d__ | 名字 | 状态 |
|---|---|---|
| 26 | `Start` | declared |
| 30 | `LoginVerify2FA` | **absent** |
| 28 | `ScrapeCaptchaKey` | **absent** |
| 31 | `EnableTwoFactor` | mentioned |
| 32 | `Register` | declared |
| 34 | `CheckFanRewardState` | **absent** |
| 36 | `ClearCart` | declared |
| 334 | `FetchBalance` | declared |
| 35 | `SignUpFanRewards` | **absent** |
| 378 | `FindEarlyAccessProduct` | **absent** |
| 38 | `RedeemExclusiveAccess` | **absent** |
| 39 | `VerifyPendingRedemption` | **absent** |
| 43 | `EnterSweepStakesRaffle` | **absent** |
| 40 | `GetSweepStakeCheckout` | **absent** |
| 41 | `GetSweepStakesShippingMethod` | **absent** |
| 42 | `SubmitSweepStakesShipping` | **absent** |
| 44 | `FindProduct` | declared |
| 46 | `AddToCartDummy` | **absent** |
| 47 | `AddToCartMulti` | **absent** |
| 45 | `GetProduct` | declared |
| 48 | `RemoveDummy` | **absent** |
| 49 | `RemoveItem` | declared |
| 51 | `ApplyDiscount` | declared |
| 54 | `CheckCart` | **absent** |
| 50 | `GetCsrf` | declared |
| 52 | `GetShippingRates` | declared |
| 53 | `SubmitShipping` | declared |
| 55 | `SubmitPayPal` | declared |
| 56 | `SubmitBilling` | declared |
| 58 | `EnterRaffle` | declared |
| 57 | `GetRaffle` | declared |
| 61 | `ResetPassword` | declared |
| 62 | `SubmitPassword` | declared |

## 组 34 · `0x143372AEA`

| d__ | 名字 | 状态 |
|---|---|---|
| 22 | `Start` | declared |
| 24 | `GetHome` | declared |
| 25 | `FindProduct` | declared |
| 26 | `GetProductHtml` | **absent** |
| 27 | `FindVariant` | declared |
| 28 | `AddToCartPreload` | declared |
| 29 | `EditLine` | declared |
| 30 | `SubmitEmail` | declared |
| 31 | `GetShippingRate` | declared |
| 32 | `SubmitShipping` | declared |
| 33 | `SubmitBilling` | declared |
| 34 | `SubmitOrder` | declared |
| 35 | `CompleteOrder` | **absent** |
| 36 | `GetCartCsrf` | **absent** |
| 37 | `GetPayPalOrderId` | declared |
| 6 | `StartShopApp` | **absent** |
| 7 | `GetAppCartToken` | **absent** |
| 14 | `ShopAddToCart` | **absent** |
| 90 | `ShopFindProduct` | **absent** |
| 13 | `ShopLogin` | **absent** |
| 102 | `ShopScrapePreload` | **absent** |
| 112 | `ShopScrapeProducts` | **absent** |
| 12 | `ShopScrapeVariants` | **absent** |
| 79 | `PropertyChanged` | mentioned |
| 88 | `AddToCart` | declared |
| 86 | `GetApiKey` | **absent** |
| 87 | `GetPaymentToken` | declared |
| 85 | `SubmitPassword` | declared |
| 89 | `UpdateCart` | **absent** |
| 90 | `AddToCartPreload` | declared |
| 91 | `HandleOutOfStock` | declared |
| 102 | `GetCustomerAccountToken` | **absent** |
| 92 | `SubmitBeacon` | **absent** |
| 106 | `AddToCartGraphQL` | **absent** |
| 1050 | `CartApiObjectCreate` | **absent** |
| 1046 | `GetAccessToken` | declared |
| 1072 | `AddToCartPreloadGraphQL` | mentioned |
| 108 | `CreateCartGraphql` | **absent** |
| 109 | `GetCartAvailabilityGraphql` | **absent** |
| 112 | `Login` | declared |
| 114 | `RefreshEmailLogin` | mentioned |
| 117 | `AccountLogin` | declared |
| 125 | `CompletePayPalPayment` | **absent** |
| 115 | `EmailLogin` | declared |
| 127 | `CompleteForwardPayment` | **absent** |
| 126 | `CompletePayPalGuestPayment` | mentioned |
| 132 | `ProcessExternalPayment` | **absent** |
| 139 | `FindAvailability` | **absent** |
| 1380 | `FindProduct` | declared |
| 143 | `SolveQuestions` | **absent** |
| 144 | `GetProperty` | declared |
| 145 | `ScrapePreload` | declared |
| 146 | `ScrapeJson` | declared |
| 147 | `ScrapeJsonAvailability` | **absent** |
| 148 | `ScrapeProduct` | declared |
| 149 | `ScrapeProductAvailability` | **absent** |
| 153 | `FindProductApp` | **absent** |
| 152 | `FindProductByHandle` | **absent** |
| 150 | `ScrapeVariantAvailability` | declared |
| 1516 | `ScrapeVariantAvailabilityApp` | **absent** |
| 156 | `CheckPriceLimit` | declared |
| 1542 | `ScrapePreloadApp` | **absent** |
| 155 | `ScrapeSellingPlan` | **absent** |
| 157 | `CheckPriceLimitApp` | declared |

## 组 35 · `0x1433779BB`

| d__ | 名字 | 状态 |
|---|---|---|
| 43 | `Start` | declared |
| 44 | `CreateCheckout` | declared |
| 45 | `GetCheckpointData` | **absent** |
| 46 | `GetSessionToken` | **absent** |
| 478 | `PreloadCheckout` | **absent** |
| 52 | `SubmitDetailsCommerce` | **absent** |
| 53 | `SubmitDiscount` | declared |
| 54 | `SubmitDiscount` | declared |
| 55 | `SubmitOrderCommerce` | **absent** |
| 56 | `CreatePayPalToken` | **absent** |
| 576 | `GetPayPalDetails` | **absent** |
| 58 | `ProcessOrderCommerce` | **absent** |
| 60 | `PollReceipt` | **absent** |
| 63 | `GenerateVariables` | **absent** |
| 620 | `RefreshSession` | declared |
| 61 | `StartInvoiceCheckout` | **absent** |
| 94 | `BuildDestination` | declared |
| 90 | `StartAppCommerce` | **absent** |
| 95 | `GetPickupGeolocation` | **absent** |
| 101 | `GetAtlasSessionToken` | **absent** |
| 102 | `GetAtlasPickupPoint` | **absent** |

## 组 36 · `0x14337998D`

| d__ | 名字 | 状态 |
|---|---|---|
| 25 | `GetProduct` | declared |
| 26 | `Login` | declared |
| 27 | `ClearCart` | declared |
| 28 | `FindProduct` | declared |
| 29 | `Preload` | mentioned |
| 30 | `AddToCart` | declared |
| 31 | `EditLine` | declared |
| 32 | `GetCsrf` | declared |
| 33 | `SubmitShipping` | declared |
| 34 | `SubmitDiscount` | declared |
| 35 | `SubmitBilling` | declared |
| 36 | `SubmitOrder` | declared |
| 42 | `Start` | declared |
| 44 | `GetProduct` | declared |
| 46 | `SubmitShipping` | declared |
| 45 | `WaitRestock` | **absent** |
| 47 | `ApplyDiscount` | declared |
| 50 | `GetPaymentToken` | declared |
| 51 | `SubmitPayment` | declared |
| 53 | `ApplyPayPal` | **absent** |
| 55 | `Process3DS` | declared |
| 57 | `ProcessOrder` | declared |
| 54 | `ProcessPayPal` | **absent** |
| 56 | `SubmitOrder` | declared |
| 52 | `SubmitPayPal` | declared |
| 58 | `ProcessDeferredPayment` | **absent** |
| 69 | `Login` | declared |
| 72 | `Authorize` | **absent** |
| 71 | `CheckSession` | **absent** |
| 70 | `Login_EnsureTaskAlive` | declared |
| 74 | `Authenticate` | declared |
| 73 | `Lookup` | mentioned |
| 75 | `SubmitTwoFactor` | **absent** |
| 76 | `Check` | declared |
| 77 | `GetToken` | declared |
| 78 | `RefreshSession` | declared |

## 组 37 · `0x14337BDA2`

| d__ | 名字 | 状态 |
|---|---|---|
| 56 | `Start` | declared |
| 63 | `CheckLogin` | declared |
| 58 | `StartClearFlow` | **absent** |
| 59 | `StartInStoreFlow` | **absent** |
| 61 | `StartNormalFlow` | **absent** |
| 60 | `StartPopNowFlow` | **absent** |
| 57 | `StartSignupFlow` | mentioned |
| 65 | `SendTwoFactor` | declared |
| 67 | `Register` | declared |
| 68 | `GetConfig` | **absent** |
| 69 | `GetSession` | declared |
| 70 | `Login` | declared |
| 71 | `Login_EnsureTaskAlive` | declared |
| 72 | `CanPlaceOrder` | mentioned |
| 74 | `FindProduct` | declared |
| 73 | `FindProductMulti` | declared |
| 77 | `ClearCart` | declared |
| 76 | `FindProductInstore` | **absent** |
| 752 | `FindProductMultiInstore` | mentioned |
| 78 | `AddToCart` | declared |
| 79 | `GetCartDataList` | **absent** |
| 80 | `GetCartId` | **absent** |
| 81 | `PollRestockMulti` | **absent** |
| 82 | `PollRestockSafe` | **absent** |
| 864 | `AddToCartBox` | **absent** |
| 83 | `ExtractPopNow` | mentioned |
| 89 | `FetchAddress` | **absent** |
| 88 | `PreviewBoxes` | **absent** |
| 85 | `SelectMultiPopNow` | **absent** |
| 87 | `SelectMultiPopNowUS` | **absent** |
| 840 | `SelectPopNow` | **absent** |
| 90 | `CalculateTaxes` | declared |
| 95 | `CreateOrder` | **absent** |
| 92 | `FetchCoupons` | **absent** |
| 93 | `FetchPromotions` | **absent** |
| 91 | `FetchRates` | **absent** |
| 94 | `SubmitDiscount` | declared |
| 960 | `SubmitOrder` | declared |
| 97 | `SubmitOrderStripe` | **absent** |
| 102 | `ClearAddresses` | **absent** |
| 98 | `GetPayPalToken` | declared |
| 994 | `ProcessOrder` | declared |
| 100 | `ProcessOrderStripe` | **absent** |
| 101 | `SubmitKakaoPay` | **absent** |
| 118 | `CheckDraw` | **absent** |
| 1204 | `CheckResult` | **absent** |
| 1354 | `ChooseGoods` | **absent** |
| 119 | `EnterDraw` | **absent** |
| 134 | `EnterDrawEvent` | **absent** |
| 1428 | `EnterExhibit` | **absent** |
| 153 | `EnterReservation` | **absent** |
| 1380 | `FetchAliases` | **absent** |
| 150 | `FetchDetails` | **absent** |
| 151 | `FindDates` | **absent** |
| 117 | `FindDraw` | **absent** |
| 132 | `FindDrawEvent` | **absent** |
| 141 | `FindExhibit` | **absent** |
| 133 | `FindMegaDraw` | **absent** |
| 1520 | `FindTimeSlots` | **absent** |
| 105 | `GetInstoreOrders` | **absent** |
| 1040 | `GetOrders` | declared |
| 137 | `RedeemLuckPoints` | **absent** |
| 1360 | `RedeemMemberPoints` | **absent** |
| 116 | `StartDrawCheckFlow` | **absent** |
| 131 | `StartDrawEventFlow` | **absent** |
| 1154 | `StartDrawFlow` | **absent** |
| 139 | `StartExhibitFlow` | **absent** |
| 149 | `StartReservationFlow` | **absent** |
| 168 | `StartRpcFlow` | mentioned |
| 1744 | `RpcCalculateShipping` | **absent** |
| 171 | `RpcCheckStock` | **absent** |
| 1738 | `RpcCreateAddress` | **absent** |
| 1768 | `RpcCreateOrder` | **absent** |
| 1720 | `RpcFetchAddress` | **absent** |
| 170 | `RpcFindProduct` | **absent** |
| 177 | `RpcGetPaymentMethods` | **absent** |
| 169 | `RpcLogin` | mentioned |
| 178 | `RpcSubmitCard` | **absent** |
| 175 | `RpcValidateBuyRule` | **absent** |
| 181 | `RpcSolveThreeDS` | **absent** |
| 182 | `RpcSubmitAdyenDetails` | **absent** |
| 183 | `RpcInitiatePayPal` | **absent** |
| 184 | `RpcCapturePayPal` | **absent** |
| 186 | `StartTasksFlow` | mentioned |
| 187 | `FetchTasks` | **absent** |
| 1886 | `StartDailyCheckInTask` | **absent** |
| 189 | `StartPopNowViewTask` | **absent** |
| 190 | `FetchPopNowSpuIds` | **absent** |
| 191 | `ViewPopNow` | **absent** |
| 192 | `ClaimReward` | mentioned |

## 组 38 · `0x143380569`

| d__ | 名字 | 状态 |
|---|---|---|
| 21 | `Start` | declared |
| 23 | `GetHome` | declared |
| 24 | `CheckVerification` | mentioned |
| 25 | `SubmitSaleRegistration` | mentioned |
| 26 | `CheckLogin` | declared |
| 27 | `Register` | declared |
| 28 | `CompleteRegistration` | declared |
| 30 | `GetCart` | declared |
| 31 | `ClearCart` | declared |
| 32 | `FindProduct` | declared |
| 33 | `AddToCart` | declared |
| 34 | `ReplaceProduct` | **absent** |
| 35 | `GetCsrf` | declared |
| 36 | `SubmitEmail` | declared |
| 37 | `GetForm` | **absent** |
| 38 | `SubmitShipping` | declared |
| 39 | `SubmitBilling` | declared |
| 16 | `Start` | declared |
| 17 | `StartCore` | mentioned |
| 22 | `AddToCart` | declared |
| 21 | `FindProduct` | declared |
| 20 | `FindProductMulti` | declared |
| 19 | `GetHome` | declared |
| 23 | `SubmitDiscount` | declared |
| 24 | `GetCsrf` | declared |
| 27 | `SendManualNotification` | **absent** |
| 26 | `SubmitOrder` | declared |
| 25 | `SubmitShipping` | declared |
| 18 | `Register` | declared |
| 19 | `AddAddress` | **absent** |
| 20 | `Login` | declared |
| 25 | `AddToCart` | declared |
| 260 | `ClearCart` | declared |
| 21 | `GetPaymentToken` | declared |
| 24 | `GetProduct` | declared |
| 28 | `GetProductDetails` | **absent** |
| 226 | `GetSession` | declared |
| 23 | `GetVerificationToken` | **absent** |
| 32 | `StartPayPalExpress` | **absent** |
| 29 | `SubmitEmail` | declared |
| 30 | `SubmitGift` | **absent** |
| 312 | `SubmitPayPal` | declared |
| 34 | `SubmitBilling` | declared |
| 356 | `SubmitPayment` | declared |

## 组 39 · `0x14338251D`

| d__ | 名字 | 状态 |
|---|---|---|
| 25 | `Start` | declared |
| 29 | `AddToBasket` | **absent** |
| 27 | `GetProduct` | declared |
| 30 | `GetSummary` | **absent** |
| 31 | `LookupAddress` | **absent** |
| 28 | `PollRestock` | **absent** |
| 33 | `GetCalendar` | **absent** |
| 37 | `GetCaptureContext` | **absent** |
| 32 | `SaveAddress` | **absent** |
| 360 | `SaveContact` | **absent** |
| 35 | `SetThirdPartyTimeslot` | **absent** |
| 348 | `SetTimeslot` | **absent** |
| 40 | `CompletePayment` | declared |
| 39 | `SubmitOrder` | declared |
| 38 | `Tokenize` | declared |
| 41 | `CardinalInit` | mentioned |
| 42 | `CardinalContinue` | mentioned |

## 组 40 · `0x143383281`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `SetAdyenPayment` | **absent** |
| 7 | `SubmitAdyenOrder` | **absent** |
| 8 | `GetAdyenPaymentStatus` | **absent** |
| 10 | `HandleAdyenAction` | **absent** |
| 90 | `HandleAdyenResult` | **absent** |
| 39 | `Start` | declared |
| 40 | `Login` | declared |
| 41 | `ClearCart` | declared |
| 42 | `GetCustomerToken` | **absent** |
| 47 | `AddToCart` | declared |
| 46 | `CreateCart` | declared |
| 45 | `FindProduct` | declared |
| 43 | `GetHome` | declared |
| 44 | `ResolveSku` | **absent** |
| 49 | `GetCheckoutPage` | **absent** |
| 50 | `GetShippingRates` | declared |
| 48 | `SetEmail` | declared |
| 52 | `SetPayment` | **absent** |
| 53 | `SubmitOrder` | declared |
| 51 | `SubmitShipping` | declared |
| 55 | `LogBadRequest` | declared |
| 73 | `GetCardNonce` | **absent** |
| 74 | `SquareHydrate` | **absent** |
| 75 | `SquareCardNonce` | **absent** |
| 890 | `CreateStripePaymentMethod` | **absent** |
| 87 | `GetStripeConfiguration` | **absent** |
| 91 | `HandleRequiresAction` | **absent** |
| 88 | `SetStripePayment` | **absent** |
| 906 | `SubmitStripeOrder` | **absent** |
| 93 | `GetStripePaymentIntent` | declared |
| 990 | `CreateUnzerResource` | **absent** |
| 984 | `SetUnzerPayment` | declared |
| 100 | `SubmitUnzerOrder` | **absent** |
| 101 | `HandleUnzerRedirect` | **absent** |
| 102 | `RunUnzerThreeDs` | **absent** |
| 103 | `ContinueUnzerThreeDs` | mentioned |
| 105 | `WalkUnzerReturn` | **absent** |
| 107 | `GetUnzerCallback` | mentioned |

## 组 41 · `0x143385F1B`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `Start` | declared |
| 7 | `GetHome` | declared |
| 10 | `AddToCart` | declared |
| 9 | `FindProduct` | declared |
| 11 | `GetCheckout` | declared |
| 8 | `Login` | declared |
| 13 | `SubmitRate` | **absent** |
| 12 | `SubmitShipping` | declared |
| 40 | `Start` | declared |
| 42 | `Authorize` | **absent** |
| 44 | `FindVariant` | declared |
| 43 | `GetAccessToken` | declared |
| 41 | `StartEcomSession` | mentioned |
| 45 | `SelectVariant` | **absent** |
| 54 | `BeginCheckout` | **absent** |
| 55 | `CheckInventory` | **absent** |
| 46 | `CreateBasket` | declared |
| 57 | `GetPaymentMethods` | **absent** |
| 516 | `GetShippingMethods` | **absent** |
| 560 | `GetShopperIp` | **absent** |
| 53 | `SubmitBillingAddress` | **absent** |
| 48 | `SubmitCustomer` | **absent** |
| 58 | `SubmitOrder` | declared |
| 502 | `SubmitShippingAddress` | **absent** |
| 526 | `SubmitShippingMethod` | **absent** |
| 498 | `ValidateAddress` | **absent** |
| 59 | `Handle3DS` | declared |

## 组 45 · `0x143389DBB`

| d__ | 名字 | 状态 |
|---|---|---|
| 10 | `Start` | declared |
| 16 | `CreateTransaction` | **absent** |
| 11 | `FindProductFlow` | declared |
| 12 | `GetCheckout` | declared |
| 13 | `GetShippingRate` | declared |
| 150 | `GetStructureToken` | **absent** |
| 18 | `ProcessPayment` | **absent** |
| 17 | `SubmitPayment` | declared |
| 140 | `SubmitShipping` | declared |
| 25 | `GetGeoLocation` | **absent** |
| 26 | `GetStoreId` | **absent** |
| 27 | `SubmitStore` | **absent** |
| 29 | `AddToCartMulti` | **absent** |
| 28 | `Login` | declared |
| 30 | `RemoveItem` | declared |
| 33 | `ApplyDiscount` | declared |
| 380 | `CaptureCard` | **absent** |
| 39 | `EarlyTokenization` | **absent** |
| 32 | `GetCheckout` | declared |
| 37 | `GetCommercehubCredentials` | **absent** |
| 31 | `GetCsrf` | declared |
| 34 | `GetShippingRates` | declared |
| 43 | `SubmitBillingInformation` | **absent** |
| 444 | `SubmitOrder` | declared |
| 36 | `SubmitPaymentDetails` | **absent** |
| 356 | `SubmitShippingInformation` | **absent** |

## 组 47 · `0x14338C233`

| d__ | 名字 | 状态 |
|---|---|---|
| 25 | `ClearCart` | declared |
| 24 | `Login` | declared |
| 26 | `GetCheckout` | declared |
| 29 | `AddToCartPreload` | declared |
| 27 | `FindProduct` | declared |
| 28 | `FindVariant` | declared |
| 30 | `EditLine` | declared |
| 36 | `GetPayPalOrderId` | declared |
| 31 | `SubmitEmail` | declared |
| 37 | `GetPayPalResult` | **absent** |
| 40 | `PollRelease` | declared |
| 38 | `PollRestock` | **absent** |
| 39 | `PollRestock2` | **absent** |

## 组 48 · `0x14338CC84`

| d__ | 名字 | 状态 |
|---|---|---|
| 11 | `Start` | declared |
| 13 | `FindProduct` | declared |
| 14 | `FindVariant` | declared |
| 16 | `GetCheckout` | declared |
| 17 | `GetShippingRates` | declared |
| 18 | `SubmitShipping` | declared |
| 19 | `GetPaymentToken` | declared |
| 20 | `SubmitCreditCard` | **absent** |
| 6 | `FindProduct` | declared |
| 7 | `AddToCart` | declared |
| 8 | `GetCheckout` | declared |
| 10 | `SubmitBilling` | declared |
| 11 | `SubmitOrder` | declared |
| 9 | `SubmitShipping` | declared |
| 12 | `HandleOrderResult` | **absent** |
| 13 | `PayerAuthenticate` | **absent** |
| 14 | `Start` | declared |
| 26 | `AddToCart` | declared |
| 19 | `FindProduct` | declared |
| 18 | `GetHome` | declared |
| 28 | `CreateCheckout` | declared |
| 27 | `GetCart` | declared |
| 29 | `SubmitAddress` | **absent** |
| 34 | `SubmitPayment` | declared |
| 35 | `SubmitThreeDSAuthentication` | **absent** |
| 36 | `FinalizeCheckout` | **absent** |

## 组 49 · `0x14338E2D6`

| d__ | 名字 | 状态 |
|---|---|---|
| 24 | `RequestSmsCode` | **absent** |
| 29 | `AddToCart` | declared |
| 27 | `GetCurrency` | **absent** |
| 28 | `GetProduct` | declared |
| 26 | `GetSession` | declared |
| 25 | `ValidateSmsCode` | **absent** |
| 31 | `CreateOrder` | **absent** |
| 30 | `Login` | declared |
| 346 | `StartPayPal` | **absent** |
| 33 | `SubmitPayment` | declared |
| 22 | `GetHome` | declared |
| 23 | `Login` | declared |
| 366 | `GetPaymentDetails` | **absent** |
| 31 | `GetPaymentToken` | declared |
| 29 | `GetShippingRates` | declared |
| 24 | `SearchProduct` | **absent** |
| 33 | `StartPayment` | **absent** |
| 350 | `StartPaymentGCash` | **absent** |
| 340 | `StartPaymentSG` | **absent** |
| 32 | `SubmitPayment` | declared |
| 37 | `SubmitPaymentDetails` | **absent** |
| 30 | `SubmitShipping` | declared |
| 38 | `CompletePayment` | declared |

## 组 50 · `0x14338F68C`

| d__ | 名字 | 状态 |
|---|---|---|
| 24 | `GetIovationParameters` | **absent** |
| 238 | `GetProductZgwMobile` | **absent** |
| 27 | `AddToCart` | declared |
| 29 | `GetCartValue` | **absent** |
| 25 | `GetHome` | declared |
| 35 | `SendManualNotification` | **absent** |
| 32 | `SubmitBilling` | declared |
| 28 | `SubmitDiscount` | declared |
| 33 | `SubmitInfo` | **absent** |
| 31 | `SubmitShipping` | declared |
| 46 | `GetPayPalNonce` | **absent** |
| 45 | `InitializePayPal` | **absent** |
| 520 | `AddToCartApp` | **absent** |
| 54 | `GetCartValueApp` | **absent** |
| 51 | `GetSessionApp` | **absent** |
| 50 | `StartApp` | mentioned |
| 58 | `SubmitBillingApp` | **absent** |
| 53 | `SubmitDiscountApp` | **absent** |
| 560 | `SubmitEmailApp` | **absent** |
| 55 | `SubmitInfoApp` | **absent** |
| 59 | `SubmitOrderApp` | **absent** |
| 57 | `SubmitShippingApp` | **absent** |

## 组 53 · `0x143392611`

| d__ | 名字 | 状态 |
|---|---|---|
| 21 | `AddToCart` | declared |
| 20 | `FindVariant` | declared |
| 22 | `GetShippingRates` | declared |
| 25 | `InitialisePayment` | **absent** |
| 23 | `RegisterCustomer` | **absent** |
| 28 | `SubmitAdyenPayment` | **absent** |
| 272 | `SubmitHpsPayment` | **absent** |
| 26 | `SubmitPayment` | declared |
| 240 | `SubmitShipping` | declared |
| 29 | `InitialisePayPal` | **absent** |
| 31 | `SubmitOrder` | declared |
| 30 | `SubmitPaypal` | **absent** |

## 组 54 · `0x14339309B`

| d__ | 名字 | 状态 |
|---|---|---|
| 14 | `CreateCheckout` | declared |
| 18 | `GetPaymentUrl` | **absent** |
| 17 | `InitalizePayment` | **absent** |
| 202 | `SubmitExternalPayment` | **absent** |
| 198 | `SubmitPayment` | declared |
| 21 | `SubmitWebComponent` | **absent** |
| 29 | `SetupTask` | **absent** |
| 30 | `Start` | declared |
| 40 | `AddToCart` | declared |
| 370 | `AddToCartApp` | **absent** |
| 38 | `CreateCheckoutApp` | **absent** |
| 35 | `FindProductApp` | **absent** |
| 39 | `GetBasket` | **absent** |
| 440 | `GetCollectPlusLocations` | **absent** |
| 43 | `GetDelivery` | **absent** |
| 33 | `GetHome` | declared |
| 50 | `GetPaymentUrl` | **absent** |
| 34 | `GetProduct` | declared |
| 36 | `GetSessionApp` | **absent** |
| 42 | `LookupAddress` | **absent** |
| 49 | `StartPayment` | **absent** |
| 48 | `SubmitBilling` | declared |
| 45 | `SubmitCollectPlus` | **absent** |
| 47 | `SubmitDelivery` | **absent** |
| 41 | `SubmitDiscount` | declared |
| 53 | `ProcessPayment` | **absent** |
| 54 | `StartPayPal` | **absent** |
| 52 | `ThreeDS` | declared |

## 组 55 · `0x14339461C`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `GetHome` | declared |
| 7 | `Login` | declared |
| 11 | `AddToCart` | declared |
| 10 | `CreateCart` | declared |
| 8 | `FindProduct` | declared |
| 9 | `GetProduct` | declared |
| 15 | `ProcessOrder` | declared |
| 14 | `SubmitOrder` | declared |
| 13 | `SubmitPayment` | declared |
| 7 | `Start` | declared |
| 9 | `AddToCart` | declared |
| 14 | `CreatePayment` | **absent** |
| 13 | `SubmitBilling` | declared |
| 10 | `SubmitDiscount` | declared |
| 11 | `SubmitEmail` | declared |
| 15 | `SubmitPayment` | declared |
| 164 | `Process` | declared |
| 11 | `GetRegisterPage` | **absent** |
| 126 | `Register` | declared |
| 17 | `CreateCheckout` | declared |
| 19 | `SubmitRate` | **absent** |
| 20 | `GetToken` | declared |
| 22 | `SubmitOrder` | declared |
| 21 | `TokenizeCard` | **absent** |
| 35 | `Start` | declared |
| 36 | `LoadCampaign` | **absent** |
| 37 | `StartCampaign` | **absent** |
| 38 | `SubmitEntry` | **absent** |
| 430 | `RestartSession` | **absent** |
| 4 | `Start` | declared |
| 8 | `SubmitKlaviyoBulkEvents` | declared |
| 7 | `SubmitKlaviyoEvent` | **absent** |
| 60 | `SubmitKlaviyoProfile` | **absent** |
| 54 | `SubmitSignup` | **absent** |
| 13 | `FindRegistration` | declared |
| 14 | `WaitForWaitlist` | **absent** |
| 15 | `FindSlot` | declared |
| 16 | `SignUp` | declared |
| 34 | `ConfirmStripeSetup` | **absent** |
| 332 | `CreateSetupIntent` | **absent** |
| 310 | `GetRaffleProduct` | declared |
| 320 | `ScrapeProductPage` | **absent** |
| 408 | `RaffleOrder` | **absent** |
| 37 | `RaffleVerification` | **absent** |
| 362 | `SolveRecaptcha` | **absent** |
| 35 | `VerifyStripeChallenge` | **absent** |
| 38 | `WaitForVerificationCode` | **absent** |

## 组 56 · `0x1433973D0`

| d__ | 名字 | 状态 |
|---|---|---|
| 2 | `Start` | declared |
| 4 | `CheckPriceLimit` | declared |
| 3 | `ScrapeProduct` | declared |
| 5 | `AddToCartStoreFront` | declared |
| 6 | `RefreshSession` | declared |
| 2 | `AccountLogin` | declared |
| 3 | `EmailLogin` | declared |
| 1 | `AccountLogin` | declared |
| 4 | `AddToCartStoreFront` | declared |
| 5 | `RefreshSession` | declared |
| 1 | `Start` | declared |
| 2 | `AddToCartStoreFront` | declared |
| 3 | `RefreshSession` | declared |
| 1 | `ScrapeJson` | declared |
| 12 | `ConfirmSubscription` | **absent** |
| 90 | `GetRaffleConfig` | **absent** |
| 8 | `GetRaffleData` | declared |
| 114 | `GetTurnstile` | **absent** |
| 10 | `SubmitRaffleEntry` | **absent** |
| 3 | `Start` | declared |
| 6 | `EnterRaffle` | declared |
| 4 | `GetRaffleData` | declared |
| 8 | `GetHome` | declared |
| 9 | `ParseScript` | **absent** |
| 10 | `GetToken` | declared |
| 11 | `PollQueue` | declared |
| 10 | `ScrapeRaffleForm` | declared |
| 116 | `SubmitKlaviyoBulkEvents` | declared |
| 13 | `SubmitKlaviyoEvent` | **absent** |
| 122 | `SubmitKlaviyoProfile` | **absent** |
| 14 | `SubmitKlaviyoSubscription` | **absent** |
| 150 | `CheckBotNot` | **absent** |
| 17 | `CreateToken` | declared |
| 16 | `GetProductDetails` | **absent** |
| 21 | `StartCheckout` | **absent** |
| 19 | `SubmitLabels` | **absent** |
| 20 | `SubmitSensor` | declared |
| 18 | `SubmitSession` | **absent** |
| 3 | `BuildDestination` | declared |
| 4 | `GetProperty` | declared |
| 5 | `CheckRaffleStatus` | **absent** |
| 68 | `GenerateVariables` | **absent** |
| 5 | `CheckPriceLimit` | declared |
| 3 | `FetchProductProperties` | **absent** |
| 12 | `GenerateCheckout` | **absent** |
| 11 | `GetCart` | declared |
| 138 | `GetCheckout` | declared |
| 3 | `CreateCheckout` | declared |
| 2 | `ScrapeProduct` | declared |
| 2 | `VerifyCart` | **absent** |
| 5 | `GetCartPage` | **absent** |
| 4 | `ScrapeProductPage` | **absent** |
| 3 | `VerifyCheckout` | **absent** |
| 2 | `PollRelease` | declared |
| 5 | `AccountLogin` | declared |
| 4 | `Newsletter` | mentioned |
| 32 | `FindProductStoreFront` | **absent** |
| 4 | `ScrapeUrlStoreFront` | **absent** |
| 7 | `AddToCartStoreFront` | declared |
| 62 | `ScrapeStoreFront` | **absent** |
| 10 | `AccountLogin` | declared |
| 128 | `AddToCartStoreFront` | declared |
| 140 | `CheckGiftCard` | **absent** |
| 114 | `CreateToken` | declared |
| 13 | `SubmitDetailsCommerce` | **absent** |
| 3 | `ResolveStorefrontHandle` | **absent** |
| 42 | `ReserveProduct` | **absent** |
| 5 | `AddToCart` | declared |
| 6 | `AddToCartPreload` | declared |
| 72 | `FlagValidPassword` | **absent** |
| 8 | `ResolvePasswordHash` | **absent** |
| 8 | `CheckPreOrderState` | **absent** |
| 46 | `ConsumeRegionRedirect` | **absent** |
| 10 | `GetRaffle` | declared |
| 70 | `RefreshSession` | declared |
| 5 | `ResolveEarlyAccessUrl` | **absent** |
| 36 | `SetLocalization` | **absent** |
| 11 | `Enter` | declared |
| 2 | `GetProperty` | declared |
| 7 | `AccountLogin` | declared |
| 96 | `CreateCart` | declared |
| 10 | `CreateCustomCheckout` | **absent** |
| 8 | `ScrapeProduct` | declared |
| 16 | `ConfirmSubscription` | **absent** |
| 126 | `SubmitKlaviyoBulkEvents` | declared |
| 14 | `SubmitKlaviyoEvent` | **absent** |
| 132 | `SubmitKlaviyoProfile` | **absent** |
| 154 | `SubmitKlaviyoSubscription` | **absent** |
| 3 | `CheckPriceLimit` | declared |
| 5 | `ScrapeVariantAvailability` | declared |
| 80 | `ScrapeJson` | declared |
| 9 | `ScrapeJsonFrontend` | **absent** |
| 10 | `ScrapeProduct` | declared |
| 11 | `ScrapeProductAvailability` | **absent** |
| 12 | `AddToCart` | declared |
| 14 | `AddToCartFrontend` | **absent** |
| 130 | `AddToCartPreload` | declared |
| 15 | `ScrapeProductData` | **absent** |

## 组 57 · `0x14339D6DF`

| d__ | 名字 | 状态 |
|---|---|---|
| 2 | `EnterRaffle` | declared |
| 10 | `WaitForDrop` | **absent** |
| 11 | `Reserve` | mentioned |
| 12 | `GetDropSchedule` | **absent** |
| 6 | `GetRegisterSession` | **absent** |
| 11 | `RegisterEmail` | **absent** |
| 40 | `StartAccountRegistrationFlow` | mentioned |
| 12 | `Submit2FA` | **absent** |
| 13 | `CompleteRegistration` | declared |
| 19 | `EnterRaffle` | declared |
| 18 | `GetRaffle` | declared |
| 15 | `StartRaffleFlow` | mentioned |
| 21 | `AccountLogin` | declared |
| 20 | `CreateCart` | declared |
| 4 | `EmailLogin` | declared |
| 1 | `GetProperty` | declared |
| 4 | `ScrapeProduct` | declared |
| 6 | `AddToCartStoreFront` | declared |
| 1 | `FindProduct` | declared |
| 3 | `GetProperty` | declared |
| 196 | `CreateRaffleCheckout` | **absent** |
| 17 | `GetProductDetails` | **absent** |
| 186 | `SolveRecaptcha` | **absent** |
| 160 | `VisitRafflePage` | **absent** |

## 组 58 · `0x14339FBFD`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `ScrapeJson` | declared |
| 8 | `ScrapePreload` | declared |
| 7 | `ScrapeVariantAvailability` | declared |
| 4 | `ScrapeJson` | declared |
| 5 | `ScrapePreload` | declared |
| 8 | `EnterRaffle` | declared |
| 7 | `FetchFormDefinition` | **absent** |
| 62 | `ScrapeRaffleForm` | declared |
| 96 | `ConfirmEmail` | **absent** |

## 组 59 · `0x1433A0F23`

| d__ | 名字 | 状态 |
|---|---|---|
| 25 | `FindProductCDN` | **absent** |
| 24 | `GetHomepagePreloadVariant` | **absent** |
| 30 | `CheckPriceLimit` | declared |
| 262 | `FindProductFrontend` | mentioned |
| 29 | `FindProductStorefront` | **absent** |
| 278 | `ScrapeJsonFrontend` | **absent** |
| 288 | `ScrapeProductFrontend` | **absent** |
| 31 | `ScrapePageFrontend` | mentioned |
| 32 | `ScrapeVariantAvailability` | declared |
| 33 | `ScrapeVariantAvailability` | declared |
| 34 | `ScrapeVariantAvailabilityFrontend` | mentioned |
| 35 | `ScrapeVariantAvailabilityStorefront` | **absent** |
| 36 | `WaitForRestock` | mentioned |
| 38 | `AddToCartStoreFront` | declared |
| 374 | `HandleOutOfStock` | declared |
| 40 | `GetAuthUrl` | **absent** |
| 39 | `GetCsrf` | declared |
| 47 | `WaitForEmailCode` | **absent** |
| 49 | `EmailLogin` | declared |
| 50 | `EnsureLogin` | **absent** |
| 51 | `RefreshLogin` | **absent** |
| 52 | `RefreshSession` | declared |

## 组 60 · `0x1433A29C0`

| d__ | 名字 | 状态 |
|---|---|---|
| 4 | `GetCartItemId` | **absent** |
| 60 | `GetStorefrontToken` | **absent** |
| 50 | `UpdateCart` | **absent** |

## 组 63 · `0x1433A6190`

| d__ | 名字 | 状态 |
|---|---|---|
| 2 | `Login` | declared |
| 3 | `AccountLogin` | declared |
| 3 | `ScrapeJson` | declared |
| 5 | `ScrapeSizes` | **absent** |
| 8 | `FindRegistration` | declared |
| 9 | `FindSlot` | declared |
| 10 | `SignUp` | declared |
| 4 | `GetCaptcha` | declared |
| 3 | `TestAI` | **absent** |
| 5 | `Test` | declared |
| 6 | `GetScore` | **absent** |
| 7 | `GetScore2` | **absent** |

## 组 64 · `0x1433AD7FE`

| d__ | 名字 | 状态 |
|---|---|---|
| 2 | `Test` | declared |
| 3 | `Test` | declared |
| 4 | `Test2` | **absent** |
| 5 | `Test3` | **absent** |
| 8 | `AuthorizePayment` | **absent** |
| 6 | `CreateIntent` | **absent** |
| 5 | `GetId` | **absent** |
| 7 | `SubmitPayment` | declared |

## 组 65 · `0x1433C0B32`

| d__ | 名字 | 状态 |
|---|---|---|
| 38 | `ClaimSlotAsync` | **absent** |
| 11 | `AcquireAsync` | mentioned |
| 9 | `SolveWafAsync` | mentioned |
| 10 | `FetchBalance` | declared |
| 12 | `ReadJsonAsync` | declared |
| 2 | `RunAsync` | declared |
| 3 | `GetActivityAsync` | **absent** |
| 7 | `CheckAsync` | declared |
| 8 | `SendAsync` | declared |
| 9 | `ClassifyAsync` | declared |

## 组 68 · `0x1433D1180`

| d__ | 名字 | 状态 |
|---|---|---|
| 2 | `AutoCompleteAsync` | **absent** |
| 9 | `CloseBufferAndWriterAsync` | **absent** |
| 8 | `DoCloseAsync` | **absent** |
| 13 | `WriteIndentAsync` | **absent** |
| 15 | `WriteValueInternalAsync` | **absent** |

## 组 70 · `0x1433D62D2`

| d__ | 名字 | 状态 |
|---|---|---|
| 43 | `ChallengeAsync` | declared |
| 70 | `Rank` | **absent** |
| 9 | `Break` | mentioned |
| 50 | `FlushAsync` | declared |
| 43 | `ReadAsync` | declared |
| 45 | `ReadAsync` | declared |
| 47 | `WriteAsync` | declared |
| 7 | `EnumerateReferences` | **absent** |

## 组 71 · `0x1433D8E3A`

| d__ | 名字 | 状态 |
|---|---|---|
| 59 | `ShowContextMenu` | **absent** |
| 60 | `UpdateContextMenu` | **absent** |
| 14 | `OnDropDownShownAsync` | **absent** |

## 组 72 · `0x1433E2F4E`

| d__ | 名字 | 状态 |
|---|---|---|
| 5 | `CallVoidFuncWhenFinishCoreAsync` | **absent** |
| 109 | `DisposeAsync` | declared |
| 11 | `FlushAsync` | declared |
| 970 | `DisposeAsyncCore` | declared |
| 122 | `EncodeCharsAsync` | **absent** |
| 1200 | `FlushAsync` | declared |
| 121 | `FlushBufferAsync` | **absent** |
| 1278 | `WriteAttributeTextBlockAsync` | **absent** |
| 113 | `WriteCharEntityAsync` | **absent** |
| 1336 | `WriteElementTextBlockAsync` | **absent** |
| 112 | `WriteEntityRefAsync` | **absent** |
| 106 | `WriteNamespaceDeclarationAsync` | **absent** |
| 118 | `WriteRawAsync` | **absent** |
| 119 | `WriteRawAsync` | **absent** |
| 144 | `WriteRawWithCharCheckingAsync` | **absent** |
| 145 | `WriteRawWithCharCheckingAsync` | **absent** |
| 107 | `WriteStartNamespaceDeclarationAsync` | **absent** |
| 116 | `WriteSurrogateCharEntityAsync` | **absent** |
| 95 | `WriteXmlDeclarationAsync` | **absent** |
| 140 | `_RawTextAsync` | **absent** |
| 129 | `_WriteAttributeTextBlockAsync` | **absent** |
| 135 | `_WriteElementTextBlockAsync` | **absent** |
| 85 | `DisposeAsyncCore` | declared |
| 1080 | `FlushAsync` | declared |
| 109 | `FlushBufferAsync` | **absent** |
| 1138 | `WriteAttributeTextBlockAsync` | **absent** |
| 101 | `WriteCharEntityAsync` | **absent** |
| 1196 | `WriteElementTextBlockAsync` | **absent** |
| 33 | `WriteEndElementAsync` | **absent** |
| 34 | `WriteEndElementAsync` | **absent** |
| 100 | `WriteEntityRefAsync` | **absent** |
| 49 | `WriteIndentAsync` | **absent** |
| 50 | `WriteIndentAsync` | **absent** |
| 94 | `WriteNamespaceDeclarationAsync` | **absent** |
| 106 | `WriteRawAsync` | **absent** |
| 107 | `WriteRawAsync` | **absent** |
| 130 | `WriteRawWithCharCheckingAsync` | **absent** |
| 131 | `WriteRawWithCharCheckingAsync` | **absent** |
| 35 | `WriteStartAttributeAsync` | **absent** |
| 36 | `WriteStartAttributeAsync` | **absent** |
| 36 | `WriteStartNamespaceDeclarationAsync` | **absent** |
| 95 | `WriteStartNamespaceDeclarationAsync` | **absent** |
| 376 | `WriteStartNamespaceDeclarationAsync` | **absent** |
| 104 | `WriteSurrogateCharEntityAsync` | **absent** |
| 83 | `WriteXmlDeclarationAsync` | **absent** |
| 126 | `_RawTextAsync` | **absent** |
| 115 | `_WriteAttributeTextBlockAsync` | **absent** |
| 1216 | `_WriteElementTextBlockAsync` | **absent** |
| 2 | `GetNonFileStreamAsync` | **absent** |
| 10 | `GetEntityAsync` | **absent** |
| 159 | `DisposeAsyncCore` | declared |
| 148 | `FlushAsync` | declared |
| 1578 | `StartElementContentAsync_WithNS` | **absent** |
| 137 | `WriteCharEntityAsync` | **absent** |
| 143 | `WriteCharsAsync` | **absent** |
| 1326 | `WriteEndAttributeAsync_SepcialAtt` | **absent** |
| 136 | `WriteEntityRefAsync` | **absent** |
| 144 | `WriteRawAsync` | **absent** |
| 145 | `WriteRawAsync` | **absent** |
| 129 | `WriteStartAttributeAsync_NoAdvanceState` | **absent** |
| 151 | `WriteStartDocumentImplAsync` | **absent** |
| 142 | `WriteStringAsync_NoAdvanceState` | **absent** |
| 1388 | `WriteSurrogateCharEntityAsync` | **absent** |
| 139 | `WriteWhitespaceAsync` | **absent** |
| 155 | `_AdvanceStateAsync_ContinueWhenFinish` | **absent** |
| 153 | `_AdvanceStateAsync_ReturnWhenFinish` | **absent** |
| 116 | `_SequenceRun` | **absent** |
| 114 | `_TryReturnTask` | **absent** |

## 组 73 · `0x1433E64DB`

| d__ | 名字 | 状态 |
|---|---|---|
| 5 | `TryDownloadThenLowercase` | **absent** |
| 2 | `DownloadFile` | **absent** |
| 4 | `DownloadString` | **absent** |
| 60 | `DownloadToStreamInternal` | **absent** |
| 13 | `DownloadReleaseEntry` | **absent** |
| 12 | `GetReleaseFeed` | declared |
| 46 | `GetReleaseFeed` | declared |

## 组 74 · `0x1433E7A69`

| d__ | 名字 | 状态 |
|---|---|---|
| 1 | `CalculateFileSHA1AndSHA256Async` | **absent** |
| 9 | `RetryAsync` | **absent** |
| 9 | `LockAsync` | mentioned |

## 组 75 · `0x14341A518`

| d__ | 名字 | 状态 |
|---|---|---|
| 57 | `CopyToAsyncCore` | **absent** |
| 272 | `DisposeAsync` | declared |
| 550 | `FlushAsyncInternal` | **absent** |
| 37 | `ReadAsyncSlowPath` | **absent** |
| 362 | `ReadFromNonSeekableAsync` | **absent** |
| 48 | `WriteAsyncSlowPath` | **absent** |
| 47 | `WriteToNonSeekableAsync` | **absent** |
| 5 | `AsyncModeCopyToAsync` | **absent** |
| 214 | `AsyncModeCopyToAsync` | **absent** |

## 组 76 · `0x14341C3F7`

| d__ | 名字 | 状态 |
|---|---|---|
| 45 | `GetInvalidControls` | **absent** |
| 212 | `CreateSheetAsync` | **absent** |
| 105 | `ObserveAsync` | mentioned |
| 29 | `ParseAsync` | declared |
| 103 | `RunScript` | **absent** |
| 42 | `ParseAsync` | declared |
| 104 | `FinishDownloadAsync` | **absent** |
| 7 | `ProcessResponseAsync` | declared |
| 9 | `WaitResponse` | **absent** |
| 5 | `ProcessResponseAsync` | declared |
| 20 | `RunAsync` | declared |
| 13 | `ProcessResponseAsync` | declared |
| 5 | `GetStyleSheets` | **absent** |
| 462 | `GetByteArrayAsyncCore` | **absent** |
| 512 | `GetStreamAsyncCore` | **absent** |
| 41 | `GetStringAsyncCore` | **absent** |
| 536 | `LoadIntoBufferAsyncCore` | **absent** |
| 70 | `WaitAndReturnAsync` | **absent** |
| 10 | `SendAsyncCore` | **absent** |
| 56 | `ApplyPlaintextFilterAsync` | **absent** |
| 538 | `ConnectAsync` | declared |
| 54 | `ConnectToTcpHostAsync` | **absent** |
| 82 | `ConstructHttp11ConnectionAsync` | **absent** |
| 103 | `ConstructHttp2ConnectionAsync` | **absent** |
| 81 | `CreateHttp11ConnectionAsync` | **absent** |
| 576 | `EstablishProxyTunnelAsync` | **absent** |
| 58 | `EstablishSocksTunnel` | **absent** |
| 105 | `HandleHttp11Downgrade` | **absent** |
| 80 | `InjectNewHttp11ConnectionAsync` | **absent** |
| 102 | `InjectNewHttp2ConnectionAsync` | **absent** |
| 52 | `SendWithVersionDetectionAndRetryAsync` | **absent** |
| 6 | `WaitForConnectionWithTelemetryAsync` | **absent** |
| 400 | `GetDigestTokenForCredential` | **absent** |
| 174 | `SendWithAuthAsync` | **absent** |
| 528 | `SendWithNtAuthAsync` | **absent** |
| 152 | `TrySetDigestAuthToken` | **absent** |
| 93 | `CopyToContentLengthAsync` | **absent** |
| 922 | `CopyToUntilEofWithExistingBufferedDataAsync` | **absent** |
| 98 | `DrainResponseAsync` | **absent** |
| 82 | `FillAsync` | declared |
| 74 | `FlushThenWriteWithoutBufferingAsync` | **absent** |
| 818 | `InitialFillAsync` | **absent** |
| 89 | `ReadBufferedAsyncCore` | **absent** |
| 56 | `SendAsync` | declared |
| 60 | `SendRequestContentAsync` | **absent** |
| 612 | `SendRequestContentWithExpect100ContinueAsync` | **absent** |
| 2 | `EstablishSslConnectionAsync` | **absent** |
| 16 | `SendAsync` | declared |
| 624 | `FlushOutgoingBytesAsync` | **absent** |
| 66 | `ProcessHeadersFrame` | **absent** |
| 64 | `ProcessIncomingFramesAsync` | **absent** |
| 84 | `ProcessOutgoingFramesAsync` | **absent** |
| 63 | `ReadFrameAsync` | declared |
| 115 | `SendAsync` | declared |
| 996 | `SendHeadersAsync` | **absent** |
| 100 | `SendStreamDataAsync` | **absent** |
| 56 | `SetupAsync` | **absent** |
| 23 | `SendAsyncMultiProxy` | **absent** |
| 4 | `SendAsync` | declared |
| 15 | `EstablishSocks4TunnelAsync` | **absent** |
| 14 | `EstablishSocks5TunnelAsync` | **absent** |
| 13 | `EstablishSocksTunnelAsync` | **absent** |
| 19 | `ReadToFillAsync` | **absent** |

## 组 77 · `0x14341F09E`

| d__ | 名字 | 状态 |
|---|---|---|
| 1 | `WaitWithCancellationAsync` | **absent** |
| 9 | `Loop` | mentioned |
| 2 | `Execute` | declared |
| 8 | `Execute` | declared |
| 1 | `TimeoutAfter` | **absent** |

## 组 78 · `0x14343377F`

| d__ | 名字 | 状态 |
|---|---|---|
| 68 | `GetConsumingEnumerable` | **absent** |
| 35 | `GetEnumerator` | declared |
| 49 | `get_Keys` | **absent** |
| 51 | `get_Values` | **absent** |

## 组 79 · `0x14343C814`

| d__ | 名字 | 状态 |
|---|---|---|
| 296 | `Selectable` | **absent** |
| 77 | `OnPasting` | **absent** |
| 13 | `Download` | mentioned |
| 12 | `Load` | declared |
| 20 | `Animate` | mentioned |
| 7 | `FadeOutAsync` | **absent** |
| 15 | `Transition` | **absent** |
| 110 | `TransitionCore` | **absent** |

## 组 80 · `0x143447729`

| d__ | 名字 | 状态 |
|---|---|---|
| 4 | `Solve` | declared |
| 52 | `GetSessionData` | **absent** |
| 10 | `ClaimBrowser` | **absent** |
| 5 | `Solve` | declared |
| 20 | `SolveAsync` | declared |
| 17 | `Solve` | declared |
| 18 | `RunWithTimeout` | **absent** |
| 20 | `LoopTurnstile` | mentioned |
| 22 | `SetCookies` | declared |
| 26 | `MoveMouse` | declared |
| 27 | `Click` | declared |
| 2 | `Solve` | declared |
| 3 | `GetScript` | declared |
| 4 | `GetSensor` | mentioned |
| 5 | `SubmitSensor` | declared |
| 3 | `SolveAsync` | declared |

## 组 81 · `0x143449937`

| d__ | 名字 | 状态 |
|---|---|---|
| 17 | `Generate` | declared |
| 21 | `GetProps1` | **absent** |
| 20 | `GetUserHash` | **absent** |
| 22 | `SubmitProps` | **absent** |
| 23 | `SubmitProps2` | **absent** |
| 25 | `SubmitSensor` | declared |
| 24 | `SubmitWpt` | **absent** |
| 26 | `FetchSensor` | **absent** |

## 组 82 · `0x14344A208`

| d__ | 名字 | 状态 |
|---|---|---|
| 32 | `Generate` | declared |
| 33 | `GetLoader` | **absent** |
| 34 | `GetCcJs` | **absent** |
| 35 | `Get6Js` | **absent** |
| 36 | `GetEtJs` | **absent** |
| 37 | `Submit` | declared |
| 9 | `Generate` | declared |
| 10 | `Sign` | mentioned |
| 9 | `SolveBotD` | mentioned |
| 20 | `PageView` | **absent** |
| 1 | `SolveAsync` | declared |
| 20 | `LogResponse` | **absent** |
| 21 | `Process` | declared |
| 22 | `ProcessSetup` | mentioned |
| 282 | `CompletePayment` | declared |
| 232 | `GetHostedPage` | mentioned |
| 24 | `GetHostedSetupPage` | **absent** |
| 25 | `GetPaymentIntent` | **absent** |
| 260 | `GetSetupIntent` | **absent** |
| 27 | `SubmitFingerprint` | **absent** |
| 4 | `GetIp` | **absent** |
| 10 | `RunAsync` | declared |
| 11 | `Init` | declared |
| 13 | `GetCookie` | **absent** |
| 12 | `GetLogo` | **absent** |
| 14 | `SubmitClientData` | **absent** |
| 15 | `SubmitPOW` | **absent** |
| 16 | `SubmitWebRtc` | **absent** |
| 17 | `Complete` | declared |
| 57 | `Bootstrap` | mentioned |
| 61 | `GetReleaseDetails` | **absent** |
| 580 | `RequestRenderMac` | **absent** |
| 62 | `RequestToken` | **absent** |
| 66 | `AuditCartAdd` | **absent** |
| 63 | `RequestSessionToken` | **absent** |
| 67 | `ValidateCheckout` | **absent** |
| 68 | `CheckInteractionChallenge` | **absent** |
| 69 | `AuditCheckoutBehaviour` | mentioned |
| 70 | `GetCartLines` | **absent** |

## 组 83 · `0x14344DF3F`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `SubmitSensor` | declared |
| 25 | `Generate` | declared |
| 26 | `Fingerprint` | declared |
| 29 | `Logo` | **absent** |
| 30 | `Decoy` | mentioned |
| 31 | `Click` | declared |

## 组 85 · `0x143452BC5`

| d__ | 名字 | 状态 |
|---|---|---|
| 42 | `MonitorExecute` | **absent** |
| 43 | `SendAsync` | declared |
| 44 | `SendCoreAsync` | **absent** |
| 45 | `SendAsync` | declared |
| 46 | `HandleRequest` | **absent** |
| 47 | `HandleResponse` | declared |
| 48 | `SetError` | **absent** |
| 24 | `GetEnumerator` | declared |

## 组 86 · `0x1434543FE`

| d__ | 名字 | 状态 |
|---|---|---|
| 13 | `HasRequested` | **absent** |
| 14 | `GetOrAddAsync` | declared |
| 15 | `Handle` | mentioned |
| 7 | `StopAsync` | declared |
| 9 | `SendCoreAsync` | **absent** |
| 51 | `GetScript` | declared |
| 52 | `GenerateCookie` | **absent** |
| 54 | `HandleBlock` | **absent** |
| 55 | `HandleResponse` | declared |
| 53 | `SetRequest` | declared |
| 2 | `HandleResponse` | declared |
| 25 | `GetScript` | declared |
| 26 | `Generate` | declared |
| 28 | `HandleResponse` | declared |
| 27 | `SetRequest` | declared |
| 8 | `SetRequest` | declared |
| 9 | `SolveBrowser` | **absent** |
| 10 | `SolveFallback` | **absent** |
| 22 | `HandleResponse` | declared |
| 24 | `RunSolverAsync` | **absent** |
| 26 | `SolveRemotelyAsync` | **absent** |
| 27 | `PrefetchAsync` | **absent** |
| 38 | `ExitSessionAsync` | **absent** |
| 40 | `PostSolverAsync` | **absent** |
| 390 | `WarmSolverAsync` | **absent** |
| 41 | `ExecuteTimedAsync` | **absent** |
| 42 | `EchoWebSocketAsync` | **absent** |
| 45 | `SetRequest` | declared |

## 组 87 · `0x14345A632`

| d__ | 名字 | 状态 |
|---|---|---|
| 48 | `GetKasada` | **absent** |
| 47 | `GetScript` | declared |
| 46 | `HandleResponse` | declared |
| 49 | `GetMfc` | mentioned |
| 50 | `GetWorkTime` | **absent** |
| 31 | `SetRequest` | declared |
| 34 | `GetKasada` | **absent** |
| 33 | `GetScript` | declared |
| 35 | `GetWorkTime` | **absent** |
| 32 | `HandleResponse` | declared |
| 0 | `SetRequest` | declared |
| 9 | `HandleResponse` | declared |
| 12 | `SolveCaptcha` | **absent** |
| 13 | `SubmitCaptcha` | **absent** |
| 11 | `SubmitPat` | mentioned |
| 14 | `SubmitChallenges` | **absent** |
| 4 | `SetRequest` | declared |
| 3 | `SetRequest` | declared |
| 18 | `HandleResponse` | declared |
| 19 | `SolveAsync` | declared |
| 22 | `CheckEvent` | **absent** |
| 21 | `Poll` | declared |
| 23 | `Solve` | declared |
| 26 | `Submit` | declared |
| 12 | `HandleResponse` | declared |
| 13 | `PollQueue` | declared |
| 2 | `SetRequest` | declared |
| 19 | `GenerateCookies` | **absent** |
| 22 | `CallParallax` | **absent** |
| 10 | `SetRequest` | declared |
| 13 | `HandleResponse` | declared |
| 5 | `HandleResponse` | declared |
| 33 | `WaitCookie` | **absent** |
| 34 | `HandleResponse` | declared |
| 35 | `SubmitRecaptchaChallenge` | **absent** |
| 36 | `SubmitPowChallenge` | **absent** |
| 37 | `SubmitBotDetectChallenge` | **absent** |
| 38 | `SubmitBotDeflectorChallenge` | mentioned |
| 39 | `SolveBotDeflectorPow` | mentioned |
| 40 | `SolveBotDeflectorIcons` | mentioned |
| 42 | `SolveBotCaptcha` | **absent** |
| 43 | `DoChallengeAsync` | **absent** |
| 47 | `GenerateJavascriptToken` | **absent** |

## 组 88 · `0x14345D905`

| d__ | 名字 | 状态 |
|---|---|---|
| 1 | `HandleResponse` | declared |
| 6 | `SetRequest` | declared |
| 7 | `EnsureFreshCsrfAsync` | **absent** |
| 19 | `HandleResponse` | declared |
| 20 | `Submit` | declared |
| 21 | `Failed` | declared |
| 10 | `RequestCompleted` | **absent** |
| 12 | `OnLoadedAsync` | **absent** |
| 11 | `RequestCompleted_Source` | **absent** |
| 13 | `NavigationFinished` | **absent** |
| 14 | `NavigationFinished_Source` | **absent** |
| 28 | `SetCookies` | declared |
| 30 | `GetCookies` | **absent** |
| 32 | `MoveMouse` | declared |
| 33 | `Click` | declared |
| 16 | `RunAsync` | declared |
| 18 | `FindFields` | **absent** |
| 28 | `FillAsync` | declared |
| 29 | `FillExpiryAsync` | **absent** |
| 30 | `FillSelectAsync` | **absent** |
| 33 | `FocusAsync` | declared |
| 35 | `ClearAsync` | declared |
| 36 | `TypeAsync` | mentioned |
| 37 | `PressAsync` | mentioned |
| 38 | `MoveMouseAsync` | declared |
| 40 | `BringIntoViewAsync` | **absent** |
| 392 | `ClickAsync` | declared |
| 17 | `AutofillAsync` | declared |
| 21 | `OnLoadedAsync` | **absent** |
| 10 | `OnLoadedAsync` | **absent** |
| 11 | `OnLoadedAsync` | **absent** |
| 44 | `Init` | declared |
| 45 | `Continue` | declared |
| 46 | `Notify` | declared |
| 47 | `SubmitCollect` | **absent** |
| 48 | `SubmitRender` | **absent** |
| 49 | `SubmitBrowserData` | **absent** |
| 52 | `SubmitMethodUrls` | **absent** |
| 53 | `SubmitCollectRedirect` | **absent** |
| 54 | `SubmitCollectRedirectV2` | **absent** |
| 55 | `Solve3DSRedirect` | declared |

## 组 89 · `0x14348BE65`

| d__ | 名字 | 状态 |
|---|---|---|
| 4 | `CropCanvasAsync` | **absent** |
| 6 | `GetCanvasFingerprintAsync` | **absent** |
| 7 | `GetFrameRectForSelectorAsync` | **absent** |
| 8 | `GetChallengeFrameRectAsync` | **absent** |
| 11 | `MoveMouseAndClickWithoutTrajectoryAsync` | **absent** |
| 13 | `MoveMouseAndClickAsync` | **absent** |
| 14 | `MoveMouseAsync` | declared |
| 17 | `PressKeyAsync` | **absent** |
| 16 | `PressMouseOnScreenAsync` | **absent** |
| 15 | `ReleaseMouseOnScreenAsync` | **absent** |

## 组 90 · `0x1434A6A7D`

| d__ | 名字 | 状态 |
|---|---|---|
| 9 | `CompletePayment` | declared |
| 10 | `GetPaymentPage` | declared |
| 11 | `GetPublicKey` | **absent** |
| 12 | `GetTemplate` | **absent** |
| 13 | `SubmitTransaction` | **absent** |
| 15 | `OpenSecurePage` | **absent** |
| 14 | `ProcessResult` | mentioned |
| 16 | `Solve3DS` | declared |
| 17 | `Navigate` | declared |
| 18 | `RunShield` | declared |
| 19 | `RunCardinal` | mentioned |

## 组 91 · `0x1434A9595`

| d__ | 名字 | 状态 |
|---|---|---|
| 9 | `ClearCart` | declared |
| 10 | `FindProduct` | declared |
| 12 | `SubmitEmail` | declared |
| 14 | `SubmitRate` | **absent** |
| 25 | `GenerateCheckout` | **absent** |
| 21 | `GetAuthToken` | declared |
| 24 | `GetBasket` | **absent** |
| 20 | `GetSession` | declared |
| 27 | `GetRates` | declared |
| 28 | `SubmitRate` | **absent** |
| 7 | `ScrapeRaffleForm` | declared |
| 96 | `SubmitKlaviyoBulkEvents` | declared |
| 11 | `SubmitKlaviyoEvent` | **absent** |
| 102 | `SubmitKlaviyoProfile` | **absent** |
| 126 | `SubmitKlaviyoSubscription` | **absent** |
| 13 | `GetProduct` | declared |
| 196 | `AddPaymentMethod` | **absent** |
| 21 | `ApplyPaymentMethod` | **absent** |
| 176 | `ConfirmShippingAddress` | **absent** |
| 16 | `ContinueAsGuest` | **absent** |
| 15 | `GetLogin` | **absent** |
| 22 | `PlaceOrder` | declared |
| 202 | `SelectBillingAddress` | **absent** |
| 18 | `SubmitShippingMethod` | **absent** |
| 17 | `LoadCheckout` | **absent** |
| 14 | `LoadProduct` | **absent** |
| 19 | `SubmitInfo` | **absent** |
| 200 | `SubmitOrder` | declared |
| 15 | `Start` | declared |
| 168 | `Login` | declared |
| 17 | `Login_EnsureTaskAlive` | declared |
| 20 | `GetBillingId` | **absent** |
| 19 | `GetShippingId` | **absent** |
| 18 | `SendTwoFactor` | declared |
| 230 | `CreateReservation` | **absent** |
| 21 | `GetDrop` | **absent** |
| 25 | `PollReservation` | **absent** |
| 220 | `SubmitCaptcha` | **absent** |
| 24 | `SubmitReservation` | **absent** |

## 组 94 · `0x1434AD998`

| d__ | 名字 | 状态 |
|---|---|---|
| 292 | `Complete3DSOrder` | **absent** |
| 36 | `GetCheckoutCaptcha` | declared |
| 37 | `Start` | declared |
| 39 | `GetProduct` | declared |
| 40 | `GetSession` | declared |
| 41 | `HandleLogin` | **absent** |
| 428 | `Login` | declared |
| 43 | `Login_EnsureTaskAlive` | declared |
| 44 | `VerifySession` | declared |
| 45 | `ClearActiveCart` | **absent** |
| 46 | `GetActiveCart` | **absent** |
| 47 | `RemoveLineItem` | declared |
| 55 | `AddPaymentToCart` | **absent** |
| 49 | `AddToCart` | declared |
| 48 | `CreateCart` | declared |
| 54 | `CreatePayment` | **absent** |
| 50 | `InitiateCheckout` | **absent** |
| 53 | `MaintainShippingGroups` | **absent** |
| 52 | `SubmitBilling` | declared |
| 62 | `AwaitDeviceProfiling` | **absent** |
| 586 | `CollectDeviceData` | **absent** |
| 570 | `SubmitCard` | **absent** |
| 63 | `SubmitOrder` | declared |
| 56 | `Tokenize` | declared |
| 64 | `Authenticate` | declared |
| 65 | `AwaitAuthentication` | **absent** |
| 66 | `GetPayment` | mentioned |
| 68 | `UpdatePayment` | **absent** |
| 69 | `HandleCartUpdate` | **absent** |

## 组 95 · `0x1434AF56E`

| d__ | 名字 | 状态 |
|---|---|---|
| 5 | `ScrapeRaffleForm` | declared |
| 66 | `SubmitKlaviyoForm` | **absent** |
| 14 | `GetCsrf` | declared |
| 16 | `ClearCart` | declared |
| 15 | `Login` | declared |
| 20 | `SubmitBilling` | declared |
| 21 | `SubmitPayment` | declared |
| 18 | `UpdateShippingMethodsList` | **absent** |
| 23 | `Process3DS` | declared |
| 30 | `CheqPageView` | **absent** |
| 32 | `ClearCart` | declared |
| 31 | `Login` | declared |
| 34 | `AddToCartPreload` | declared |
| 35 | `EditLine` | declared |
| 37 | `GetCheckoutLogin` | **absent** |
| 39 | `GetPickupStore` | **absent** |
| 40 | `SubmitPickup` | **absent** |
| 41 | `SubmitPayment` | declared |
| 42 | `PlaceOrder` | declared |
| 43 | `ProcessMulPay` | **absent** |
| 44 | `CreateGmoToken` | declared |

## 组 99 · `0x1434B407E`

| d__ | 名字 | 状态 |
|---|---|---|
| 28 | `SubmitPayment` | declared |
| 27 | `SubmitShipmentInfo` | **absent** |
| 30 | `CreateGmoToken` | declared |
| 29 | `PlaceOrder` | declared |
| 31 | `ProcessThreeDs` | declared |
| 32 | `FollowGmoRedirects` | **absent** |
| 33 | `GetCheckoutCaptcha` | declared |

## 组 101 · `0x1434B9F00`

| d__ | 名字 | 状态 |
|---|---|---|
| 77 | `DisposeAsync` | declared |
| 78 | `FlushAsync` | declared |
| 20 | `FlushAsync` | declared |
| 31 | `DisposeCompletedAsyncDisposables` | **absent** |
| 33 | `DisposePendingDisposablesOnExceptionAsync` | **absent** |

## 组 102 · `0x1434BCDD5`

| d__ | 名字 | 状态 |
|---|---|---|
| 8 | `GetGarbageCollectionCounts` | **absent** |
| 9 | `GetCpuTime` | **absent** |
| 11 | `GetHeapFragmentation` | **absent** |
| 106 | `GetHeapSizes` | **absent** |
| 276 | `DisposeClientAsync` | **absent** |
| 19 | `ConnectAsync` | declared |
| 69 | `DisposeAsync` | declared |
| 43 | `FillAsync` | declared |
| 40 | `HandshakeAsync` | **absent** |
| 44 | `ReadAsync` | declared |
| 410 | `ReadRecordAsync` | **absent** |
| 137 | `ReceiveLoopAsync` | **absent** |
| 161 | `TimerLoopAsync` | **absent** |
| 47 | `TrySendAlertAsync` | **absent** |
| 45 | `WriteAsync` | declared |
| 460 | `WriteRecordsLockedAsync` | **absent** |
| 110 | `ConnectAsync` | declared |
| 197 | `DisposeAsync` | declared |
| 111 | `OpenBidirectionalStreamAsync` | **absent** |
| 7 | `ReceiveAsync` | declared |
| 13 | `DisposeAsync` | declared |
| 10 | `ReceiveAsync` | declared |
| 41 | `ReadAtLeastAsync` | **absent** |
| 40 | `WaitForDataAsync` | **absent** |
| 1 | `ConnectOpaqueAsync` | **absent** |
| 212 | `ConnectAsync` | declared |
| 24 | `ConnectSocketAsync` | **absent** |
| 232 | `ConnectSocketAsync` | **absent** |
| 26 | `DialSerialAsync` | **absent** |
| 25 | `ResolveAsync` | declared |
| 4 | `ReadAsync` | declared |
| 0 | `ReadAsync` | declared |
| 14 | `ConnectAsync` | declared |
| 2 | `HandshakeAsync` | **absent** |
| 6 | `ReadExactAsync` | declared |
| 4 | `ReadReplyAsync` | **absent** |
| 45 | `AcceptLoopAsync` | **absent** |
| 43 | `DecodeHeadersAsync` | declared |
| 48 | `DisposeAsync` | declared |
| 47 | `HandleControlStreamAsync` | **absent** |
| 460 | `HandleUnidirectionalStreamAsync` | **absent** |
| 42 | `ReadResponseAsync` | **absent** |
| 36 | `SendAsync` | declared |
| 33 | `StartAsync` | declared |
| 44 | `WriteDecoderStreamAsync` | **absent** |
| 13 | `FillAsync` | declared |
| 186 | `ReadFrameAsync` | declared |
| 15 | `ReadFrameHeaderAsync` | **absent** |
| 16 | `ReadPayloadAsync` | **absent** |
| 17 | `ReadPayloadAsync` | **absent** |
| 19 | `ReadRawAsync` | **absent** |
| 14 | `ReadVarintAsync` | **absent** |
| 18 | `DialHttp3Async` | **absent** |
| 19 | `DialHttp3Async` | **absent** |
| 216 | `DisposeAsync` | declared |
| 17 | `DisposeWhenDoneAsync` | **absent** |
| 15 | `RunRaceAsync` | **absent** |
| 10 | `SendAsync` | declared |
| 21 | `DialSharedAsync` | **absent** |
| 32 | `DisposeAsync` | declared |
| 20 | `SendAsync` | declared |
| 29 | `SendHttp1Async` | **absent** |
| 68 | `ReadLoopAsync` | **absent** |
| 56 | `WriteLoopAsync` | **absent** |
| 584 | `DrainOutboundAsync` | **absent** |
| 71 | `HandleSettingsAsync` | **absent** |
| 61 | `SendAsync` | declared |
| 53 | `StartAsync` | declared |
| 64 | `WriteBodyAsync` | **absent** |
| 5 | `ReadExactAsync` | declared |
| 54 | `DisposeAsync` | declared |
| 49 | `FillAsync` | declared |
| 53 | `ReadChunkedAsync` | **absent** |
| 50 | `ReadExactAsync` | declared |
| 52 | `ReadIntoAsync` | **absent** |
| 488 | `ReadLineAsync` | **absent** |
| 46 | `ReadResponseHeadAsync` | **absent** |
| 51 | `ReadToEndAsync` | declared |
| 38 | `TrySkipBodyAsync` | **absent** |
| 64 | `GetEnumerator` | declared |

## 组 103 · `0x1434BFFE6`

| d__ | 名字 | 状态 |
|---|---|---|
| 3 | `CreateAsync` | declared |
| 7 | `CreateRequestParametersAsync` | **absent** |
| 8 | `InitializeCacheKeyComponentsAsync` | **absent** |
| 22 | `FilterBrokerAccountsByEnvAsync` | **absent** |
| 21 | `GetAccountsFromBrokerAsync` | **absent** |
| 20 | `GetAccountsInternalAsync` | **absent** |
| 50 | `FilterTokensByEnvironmentAsync` | **absent** |
| 61 | `GetTenantProfilesAsync` | **absent** |

## 组 104 · `0x1434C2E07`

| d__ | 名字 | 状态 |
|---|---|---|
| 113 | `DisposeAsync` | declared |
| 170 | `EnsureFullTlsFrameAsync` | **absent** |
| 159 | `ForceAuthenticationAsync` | **absent** |
| 1566 | `ProcessAuthenticationWithTelemetryAsync` | **absent** |
| 172 | `ReadAsyncInternal` | **absent** |
| 160 | `ReceiveHandshakeFrameAsync` | **absent** |
| 157 | `ReplyOnReAuthenticationAsync` | **absent** |
| 165 | `WriteAsyncChunked` | **absent** |
| 173 | `WriteAsyncInternal` | **absent** |
| 5 | `AuthenticateAsync` | declared |
| 6 | `AuthenticateAsync` | declared |
| 9 | `ConnectAsync` | declared |
| 12 | `DisconnectAsync` | declared |
| 3 | `IdentifyAsync` | **absent** |
| 14 | `IdleAsync` | **absent** |
| 134 | `NoOpAsync` | **absent** |
| 4 | `OnAuthenticatedAsync` | **absent** |
| 8 | `PostConnectAsync` | **absent** |
| 7 | `SslHandshakeAsync` | **absent** |
| 280 | `FetchStreamAsync` | **absent** |
| 193 | `GetEnumerator` | declared |
| 310 | `GetMessageAsync` | **absent** |
| 203 | `OnVanishedAsync` | **absent** |
| 302 | `OpenAsync` | declared |
| 273 | `ParseMessageAsync` | **absent** |
| 240 | `ParseSummaryItemsAsync` | **absent** |
| 2378 | `ReadDateTimeOffsetTokenAsync` | **absent** |
| 233 | `ReadLiteralDataAsync` | **absent** |
| 235 | `SkipParenthesizedListAsync` | **absent** |
| 169 | `ConnectAsync` | declared |
| 211 | `IterateAsync` | **absent** |
| 227 | `LookupParentFoldersAsync` | **absent** |
| 201 | `ParseResponseCodeAsync` | **absent** |
| 179 | `PeekTokenAsync` | **absent** |
| 181 | `PeekTokenAsync` | **absent** |
| 2078 | `ProcessUntaggedResponseAsync` | **absent** |
| 232 | `QueryNamespacesAsync` | **absent** |
| 241 | `QuerySpecialFoldersAsync` | **absent** |
| 1730 | `ReadLineAsync` | **absent** |
| 184 | `ReadLiteralAsync` | **absent** |
| 213 | `RunAsync` | declared |
| 186 | `SkipLineAsync` | **absent** |
| 85 | `StepAsync` | declared |
| 192 | `UpdateCapabilitiesAsync` | **absent** |
| 1942 | `UpdateNamespacesAsync` | **absent** |
| 204 | `UpdateStatusAsync` | **absent** |
| 10 | `WriteToAsync` | declared |
| 93 | `FlushAsync` | declared |
| 54 | `ReadAheadAsync` | **absent** |
| 594 | `ReadAsync` | declared |
| 68 | `ReadAtomStringAsync` | **absent** |
| 868 | `ReadLineAsync` | **absent** |
| 77 | `ReadLiteralTokenAsync` | **absent** |
| 65 | `ReadQuotedStringTokenAsync` | **absent** |
| 80 | `ReadTokenAsync` | **absent** |
| 90 | `WriteAsync` | declared |
| 75 | `ParseAnnotationsAsync` | **absent** |
| 57 | `ParseBodyAsync` | **absent** |
| 44 | `ParseContentDispositionAsync` | **absent** |
| 46 | `ParseContentLanguageAsync` | **absent** |
| 498 | `ParseContentLocationAsync` | **absent** |
| 42 | `ParseContentTypeAsync` | **absent** |
| 61 | `ParseEnvelopeAddressAsync` | **absent** |
| 642 | `ParseEnvelopeAddressListAsync` | **absent** |
| 68 | `ParseEnvelopeAsync` | **absent** |
| 664 | `ParseEnvelopeDateAsync` | **absent** |
| 736 | `ParseFlagsListAsync` | **absent** |
| 25 | `ParseFolderListAsync` | **absent** |
| 146 | `ParseImplementationAsync` | **absent** |
| 772 | `ParseLabelsListAsync` | **absent** |
| 284 | `ParseMetadataAsync` | **absent** |
| 53 | `ParseMultipartAsync` | **absent** |
| 394 | `ParseParameterListAsync` | **absent** |
| 198 | `ReadFolderNameAsync` | **absent** |
| 33 | `ReadNStringTokenAsync` | **absent** |
| 366 | `ReadNumberAsync` | **absent** |
| 31 | `ReadStringTokenAsync` | **absent** |
| 55 | `ShouldParseMultipartAsync` | **absent** |
| 51 | `SkipBodyExtensionAsync` | **absent** |
| 56 | `CopyToAsyncInternal` | **absent** |
| 616 | `DisposeAsyncCore` | declared |
| 30 | `FlushFinalBlockAsync` | **absent** |
| 440 | `ReadAsyncCore` | **absent** |
| 37 | `ReadAsyncInternal` | **absent** |
| 532 | `WriteAsyncCore` | **absent** |
| 47 | `WriteAsyncInternal` | **absent** |

## 组 105 · `0x1434C59BE`

| d__ | 名字 | 状态 |
|---|---|---|
| 0 | `BuildDefaultMenuItems` | **absent** |
| 66 | `ShowAsync` | declared |
| 0 | `ContainsTextAsync` | **absent** |
| 1 | `GetDataObjectAsync` | **absent** |
| 1 | `SendMultiSegmentAsync` | **absent** |
| 21 | `ConnectAsyncCore` | **absent** |
| 11 | `GetEnumerator` | declared |
| 5 | `get_Keys` | **absent** |
| 7 | `get_Values` | **absent** |
| 334 | `CompleteConnectAsync` | **absent** |
| 22 | `ConnectAsync` | declared |
| 696 | `CloseAsyncPrivate` | **absent** |
| 50 | `CloseOutputAsyncCore` | **absent** |
| 67 | `CloseWithReceiveErrorAndThrowAsync` | **absent** |
| 72 | `EnsureBufferContainsAsync` | **absent** |
| 63 | `HandleReceivedCloseAsync` | **absent** |
| 658 | `HandleReceivedPingPongAsync` | **absent** |
| 61 | `ReceiveAsyncPrivate` | **absent** |
| 70 | `SendCloseFrameAsync` | **absent** |
| 57 | `SendFrameFallbackAsync` | **absent** |
| 97 | `SendPingAsync` | **absent** |
| 648 | `WaitForServerToCloseConnectionAsync` | **absent** |
| 56 | `WaitForWriteTaskAsync` | **absent** |
| 24 | `DisposeAsync` | declared |
| 21 | `SendLoopAsync` | **absent** |
| 5 | `InsertAsync` | declared |
| 342 | `GetOwnProperties` | declared |
| 35 | `GetInitialOwnStringPropertyKeys` | **absent** |
| 38 | `GetOwnProperties` | declared |
| 85 | `Enumerate` | mentioned |
| 83 | `GetEnumerator` | declared |

## 组 106 · `0x1434CD41F`

| d__ | 名字 | 状态 |
|---|---|---|
| 49 | `EnumerateOwnPropertyKeys` | **absent** |
| 48 | `GetOwnProperties` | declared |
| 202 | `NameCreator` | **absent** |
| 6 | `WriteDeclAsync` | **absent** |
| 24 | `ReplayAsync` | mentioned |

## 组 107 · `0x1434CEA4D`

| d__ | 名字 | 状态 |
|---|---|---|
| 76 | `CloseStreamsAsync` | **absent** |
| 146 | `CloseStreamsAsync` | **absent** |
| 74 | `DisposeAsync` | declared |
| 75 | `DisposeAsyncCore` | declared |
| 130 | `GetOffsetOfCompressedDataAsync` | **absent** |
| 135 | `LoadCompressedBytesIfNeededAsync` | **absent** |
| 1344 | `LoadLocalHeaderExtraFieldIfNeededAsync` | **absent** |
| 145 | `UnloadStreamsAsync` | **absent** |
| 17 | `WriteAllBlocksAsync` | **absent** |
| 132 | `WriteAndFinishLocalEntryAsync` | **absent** |
| 82 | `WriteArchiveEpilogueAsync` | **absent** |
| 16 | `WriteBlockAsync` | **absent** |
| 133 | `WriteCentralDirectoryFileHeaderAsync` | **absent** |
| 143 | `WriteCrcAndSizesInLocalHeaderAsync` | **absent** |
| 814 | `WriteFileAsync` | **absent** |
| 142 | `WriteLocalFileHeaderAndDataIfNeededAsync` | **absent** |
| 1410 | `WriteLocalFileHeaderAsync` | **absent** |
| 120 | `GetExtraFieldsAsync` | **absent** |
| 28 | `ReadAsyncCore` | **absent** |
| 13 | `TrySkipBlockAsync` | **absent** |
| 184 | `WriteBlockAsync` | **absent** |
| 63 | `PurgeBuffersAsync` | **absent** |
| 71 | `WriteDeflaterOutputAsync` | **absent** |

## 组 109 · `0x14350E184`

| d__ | 名字 | 状态 |
|---|---|---|
| 42 | `CombinedClaimsIterator` | **absent** |
| 25 | `get_Keys` | **absent** |
| 27 | `get_Values` | **absent** |
| 115 | `GetAttributes` | **absent** |
| 38 | `GetDescendants` | **absent** |
| 39 | `GetElements` | **absent** |
| 18 | `Nodes` | mentioned |

## 组 110 · `0x14350F341`

| d__ | 名字 | 状态 |
|---|---|---|
| 23 | `EnumerateAsync` | mentioned |
| 38 | `FillLineBufferAsync` | **absent** |
| 32 | `MethodsToRegister` | **absent** |
| 31 | `TypesToRegister` | **absent** |

## 组 111 · `0x1435104C5`

| d__ | 名字 | 状态 |
|---|---|---|
| 91 | `get_Claims` | **absent** |
| 7 | `get_CustomAttributes` | **absent** |
| 24 | `AsEnumerable` | **absent** |
| 25 | `AsEnumerable` | **absent** |
| 20 | `GetTopLevelTypes` | **absent** |
| 192 | `GetTransitiveNamespaces` | **absent** |
| 21 | `GetTransitiveTypes` | **absent** |
| 2 | `get_CustomAttributes` | **absent** |
| 16 | `GetCustomAttributes` | **absent** |
| 185 | `CoreGetDeclaredSyntheticConstructors` | **absent** |
| 187 | `CoreGetDeclaredSyntheticMethods` | **absent** |
| 18 | `get_SyntheticConstructors` | **absent** |
| 20 | `get_SyntheticMethods` | **absent** |
| 4 | `get_CustomAttributes` | **absent** |

## 组 112 · `0x143512495`

| d__ | 名字 | 状态 |
|---|---|---|
| 2 | `GetMatchingCustomAttributesIterator` | **absent** |
| 4 | `CompleteCopyToAsync` | **absent** |
| 8 | `CopyToAsyncCore` | **absent** |
| 16 | `DrainAsync` | **absent** |
| 16 | `DrainOnDisposeAsync` | **absent** |
| 64 | `ReadAsyncCore` | **absent** |
| 2 | `ReadAsync` | declared |
| 5 | `CompleteCopyToAsync` | **absent** |
| 10 | `DrainAsync` | **absent** |
| 8 | `CompleteCopyToAsync` | **absent** |
| 32 | `ReadAsync` | declared |
| 98 | `CreateContentReadStreamAsyncCore` | **absent** |
| 6 | `ReadAsync` | declared |
| 6 | `SerializeToStreamAsync` | **absent** |
| 14 | `WaitWithConnectionCancellationAsync` | **absent** |
| 79 | `CopyToAsync` | declared |
| 77 | `ReadDataAsync` | **absent** |
| 74 | `ReadResponseHeadersAsync` | **absent** |
| 816 | `SendDataAsync` | **absent** |
| 45 | `SendRequestBodyAsync` | **absent** |
| 46 | `WaitFor100ContinueAsync` | **absent** |
| 25 | `GetEnumeratorCore` | **absent** |
| 6 | `SendAsyncWithMetrics` | **absent** |

## 组 113 · `0x14351D642`

| d__ | 名字 | 状态 |
|---|---|---|
| 2310 | `ExecuteLinkChange` | **absent** |
| 230 | `ExecuteQuicktask` | **absent** |
| 2218 | `ExecuteStartAll` | **absent** |
| 215 | `ExecuteStartSelected` | **absent** |
| 232 | `ReadClipboard` | **absent** |

## 组 114 · `0x14351DEA8`

| d__ | 名字 | 状态 |
|---|---|---|
| 27 | `OnKeyDown` | **absent** |
| 35 | `PublishButton_Click` | **absent** |
| 42 | `GetTemplates` | **absent** |
| 34 | `ExecuteFetchBalance` | declared |
| 15 | `ExecuteFetchBalance` | declared |
| 444 | `DragBorderPressed` | **absent** |
| 36 | `ExecuteBackup` | **absent** |
| 390 | `ExecuteExport` | **absent** |
| 41 | `Import` | declared |
| 38 | `RestoreAsync` | declared |
| 28 | `ExecuteSelectSound` | **absent** |
| 23 | `ExecuteConfigure` | mentioned |
| 15 | `ExecuteTest` | **absent** |

## 组 115 · `0x143521146`

| d__ | 名字 | 状态 |
|---|---|---|
| 42 | `YesButton_Click` | **absent** |
| 38 | `YesButton_Click` | **absent** |
| 9 | `ExecuteLogOut` | **absent** |
| 63 | `ExecuteDispose` | **absent** |
| 64 | `ExecuteCloseSolver` | **absent** |
| 11 | `Load` | declared |
| 26 | `ExecuteLogout` | **absent** |
| 38 | `ExecuteAuthenticate` | **absent** |
| 40 | `ExecuteRefresh` | **absent** |
| 53 | `ExecuteSignIn` | **absent** |
| 726 | `ExecuteLoadAnalytics` | **absent** |
| 754 | `ExecuteLoadCheckouts` | **absent** |
| 74 | `ExecuteLoadReleases` | **absent** |

## 组 116 · `0x143525B34`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `SubmitSDK` | **absent** |
| 5 | `GenerateSensor` | declared |
| 6 | `SubmitCh` | mentioned |
| 7 | `SubmitLe` | **absent** |

## 组 117 · `0x14353A8C2`

| d__ | 名字 | 状态 |
|---|---|---|
| 11 | `ReadAsync` | declared |
| 66 | `CastIAsyncEnumerable` | **absent** |
| 62 | `StartAsyncCore` | **absent** |
| 53 | `StartAsyncInner` | **absent** |
| 64 | `StopAsyncCore` | **absent** |
| 67 | `StreamAsChannelCoreAsyncCore` | **absent** |
| 75 | `CommonStreaming` | **absent** |
| 86 | `DispatchInvocationAsync` | **absent** |
| 87 | `DispatchInvocationStreamItemAsync` | **absent** |
| 94 | `HandleConnectionClose` | **absent** |
| 90 | `HandshakeAsync` | **absent** |
| 79 | `InvokeCore` | **absent** |
| 77 | `InvokeCoreAsyncCore` | **absent** |
| 80 | `InvokeStreamCore` | **absent** |
| 85 | `ProcessMessagesAsync` | **absent** |
| 918 | `ReceiveLoop` | **absent** |
| 97 | `ReconnectAsync` | **absent** |
| 83 | `SendCoreAsyncCore` | **absent** |
| 820 | `SendHubMessage` | **absent** |
| 74 | `SendStreamItemAsync` | **absent** |
| 846 | `SendWithLock` | **absent** |
| 764 | `WaitForActiveConnectionWithActivityAsync` | **absent** |
| 55 | `DisposeAsync` | declared |
| 60 | `InvokeCoreAsync` | **absent** |
| 61 | `SendCoreAsync` | **absent** |
| 52 | `StartAsync` | declared |
| 54 | `StopAsync` | declared |
| 59 | `StreamAsChannelCoreAsync` | **absent** |

## 组 118 · `0x14353BDF0`

| d__ | 名字 | 状态 |
|---|---|---|
| 43 | `InvokeCoreAsync` | **absent** |
| 31 | `ResendAsync` | **absent** |
| 29 | `AckAsync` | mentioned |
| 25 | `RunTimer` | mentioned |
| 28 | `WriteAsyncCore` | **absent** |
| 7 | `GetEnumerator` | declared |
| 8 | `GetEnumerator` | declared |
| 12 | `Candidates` | mentioned |
| 21 | `FlushAsync` | declared |
| 22 | `FlushLockedAsync` | **absent** |

## 组 119 · `0x14353D2CD`

| d__ | 名字 | 状态 |
|---|---|---|
| 1 | `GetEnumerator` | declared |
| 2 | `GetEnumerator` | declared |
| 1 | `CreateAuthorityForRequestAsync` | **absent** |
| 66 | `IsAuthorityAliasedAsync` | **absent** |
| 5 | `ValidateSameHostAsync` | **absent** |

## 组 120 · `0x14353EF23`

| d__ | 名字 | 状态 |
|---|---|---|
| 13 | `FindAccessTokenAsync` | **absent** |
| 178 | `FindFamilyRefreshTokenAsync` | **absent** |
| 18 | `FindRefreshTokenAsync` | **absent** |
| 15 | `GetAccountAssociatedWithAccessTokenAsync` | **absent** |
| 20 | `GetAccountsAsync` | **absent** |
| 166 | `GetIdTokenCacheItemAsync` | **absent** |
| 19 | `IsAppFociMemberAsync` | **absent** |
| 21 | `RefreshCacheForReadOperationsAsync` | **absent** |
| 12 | `RefreshCacheForReadOperationsIfEnabledAsync` | **absent** |
| 14 | `SaveTokenResponseAsync` | **absent** |

## 组 121 · `0x14354062E`

| d__ | 名字 | 状态 |
|---|---|---|
| 124 | `CloneHttpContentAsync` | **absent** |
| 13 | `CreateResponseAsync` | **absent** |
| 8 | `SendRequestAsync` | **absent** |
| 46 | `GetAuthorizationEndpointAsync` | **absent** |
| 11 | `GetInstanceDiscoveryEntryAsync` | **absent** |
| 3 | `GetTokenEndpointAsync` | **absent** |
| 12 | `RunInstanceDiscoveryAndValidationAsync` | **absent** |
| 14 | `ValidateAuthorityAsync` | **absent** |
| 14 | `ExecuteRequestAsync` | **absent** |
| 6 | `AddBodyParamsAndHeadersAsync` | **absent** |
| 96 | `SendHttpAndClearTelemetryAsync` | **absent** |
| 4 | `SendTokenRequestAsync` | **absent** |
| 7 | `FetchAuthCodeAndPkceInternalAsync` | **absent** |
| 4 | `FetchAuthCodeAndPkceVerifierAsync` | **absent** |
| 9 | `InvokeBackgroundRefreshCallbackAsync` | **absent** |
| 4 | `RefreshAccessTokenAsync` | **absent** |
| 4 | `GetMetadataAsync` | **absent** |
| 16 | `DiscoverAndCacheAsync` | **absent** |
| 174 | `DiscoverAsync` | **absent** |
| 11 | `GetAzureRegionAsync` | **absent** |
| 21 | `GetImdsUriApiVersionAsync` | **absent** |
| 66 | `MeasureAsync` | mentioned |
| 4 | `MeasureCodeBlockAsync` | **absent** |
| 2 | `AcquireAuthorizationAsync` | **absent** |

## 组 122 · `0x14354B0A6`

| d__ | 名字 | 状态 |
|---|---|---|
| 11 | `GetParentTypes` | **absent** |
| 6 | `CopyFromSourceToDestinationAsync` | **absent** |
| 10 | `WriteAsyncCore` | **absent** |

## 组 123 · `0x1435B3679`

| d__ | 名字 | 状态 |
|---|---|---|
| 20 | `DisposeAsync` | declared |
| 17 | `ForeachService` | **absent** |
| 14 | `StartAsync` | declared |
| 16 | `StopAsync` | declared |
| 15 | `TryExecuteBackgroundServiceAsync` | **absent** |
| 66 | `GetEnumerator` | declared |
| 18 | `GetTranscodingStreamAsync` | **absent** |
| 16 | `ReadFromJsonAsyncCore` | **absent** |
| 14 | `SerializeToStreamAsyncTranscoding` | **absent** |
| 14 | `GetAllowedCodePoints` | **absent** |
| 568 | `CoreGetDeclaredConstructors` | **absent** |
| 58 | `CoreGetDeclaredEvents` | **absent** |
| 59 | `CoreGetDeclaredFields` | **absent** |
| 57 | `CoreGetDeclaredMethods` | **absent** |
| 61 | `CoreGetDeclaredNestedTypes` | **absent** |
| 60 | `CoreGetDeclaredProperties` | **absent** |
| 4 | `get_DefinedTypes` | **absent** |

## 组 124 · `0x1435B91C4`

| d__ | 名字 | 状态 |
|---|---|---|
| 28 | `ExecuteSave` | declared |
| 78 | `ExecuteDelete` | **absent** |
| 79 | `ExecuteSave` | declared |
| 31 | `ExecuteSave` | declared |
| 34 | `ExecuteSearch` | **absent** |
| 18 | `ExecuteSave` | declared |
| 240 | `Dropped` | mentioned |
| 25 | `FileImportPressed` | **absent** |
| 26 | `Import` | declared |
| 27 | `ExecuteCopy` | **absent** |
| 186 | `ExportClick` | **absent** |
| 185 | `ImportClick` | **absent** |

## 组 126 · `0x1435BBD12`

| d__ | 名字 | 状态 |
|---|---|---|
| 29 | `FileImportPressed` | **absent** |
| 49 | `OnUserInput` | **absent** |
| 50 | `WaitForUntouchedChallengeAsync` | **absent** |
| 57 | `SharePendingAnswerAsync` | **absent** |
| 58 | `Run` | declared |
| 61 | `RunPhaseAsync` | **absent** |
| 67 | `GetImageAsync` | **absent** |
| 77 | `OnNewAnswer` | **absent** |
| 78 | `OnNewAnswer_Source` | **absent** |
| 79 | `TypeAndSubmitAnswerAsync` | **absent** |
| 80 | `TypeMessageAsync` | **absent** |
| 32 | `Run` | declared |
| 35 | `RunPhaseAsync` | **absent** |

## 组 127 · `0x1435BE9D0`

| d__ | 名字 | 状态 |
|---|---|---|
| 1 | `DeserializeAsync` | mentioned |
| 15 | `SerializeAsync` | declared |
| 12 | `SolveHintChallengeAsync` | **absent** |
| 13 | `InvokeHintLabelsAsync` | **absent** |
| 14 | `InvokeMatchApiAsync` | **absent** |
| 20 | `InvokeResolveAsync` | **absent** |

## 组 128 · `0x1435C33D8`

| d__ | 名字 | 状态 |
|---|---|---|
| 52 | `RunTimerActions` | **absent** |
| 43 | `StopAsyncCore` | **absent** |
| 45 | `TimerLoop` | **absent** |
| 25 | `WaitForActiveConnectionAsync` | **absent** |
| 46 | `WriteAsync` | declared |
| 10 | `GetEnumerator` | declared |
| 13 | `MoveNextAsyncAwaited` | **absent** |
| 10 | `GetAllValues` | **absent** |

## 组 129 · `0x1435C694B`

| d__ | 名字 | 状态 |
|---|---|---|
| 10 | `PauseForRetryAsync` | **absent** |
| 6 | `PauseForRetryAsync` | **absent** |
| 118 | `FetchNetworkMetadataOrFallbackAsync` | **absent** |
| 10 | `GetMetadataEntryAsync` | **absent** |
| 9 | `GetMetadataEntryTryAvoidNetworkAsync` | **absent** |
| 9 | `FetchAllDiscoveryMetadataAsync` | **absent** |
| 7 | `GetMetadataAsync` | **absent** |
| 10 | `SendInstanceDiscoveryRequestAsync` | **absent** |
| 2 | `GetOidcAsync` | **absent** |
| 2 | `ValidateAuthorityAsync` | **absent** |
| 9 | `ExecuteAsync` | declared |
| 108 | `FetchTokensFromBrokerAsync` | **absent** |
| 11 | `GetTokenResponseAsync` | **absent** |
| 12 | `RunBrokerWithInstallUriAsync` | **absent** |
| 28 | `CacheTokenResponseAndCreateAuthenticationResultAsync` | **absent** |
| 138 | `RunAsync` | declared |
| 31 | `SendTokenRequestAsync` | **absent** |
| 40 | `ValidateCachedAccessTokenAsync` | **absent** |
| 104 | `SendTokenRequestToBrokerAsync` | **absent** |
| 9 | `FetchTokensAsync` | **absent** |
| 0 | `ResolveAsync` | declared |
| 2 | `InitExplicitMtlsPopAsync` | **absent** |
| 7 | `InitMtlsPopParametersAsync` | **absent** |
| 0 | `TryInitAsync` | **absent** |
| 1 | `TryInitImplicitBearerOverMtlsAsync` | **absent** |
| 104 | `TryInitMtlsPopParametersAsync` | **absent** |
| 2 | `ExecuteAsync` | declared |

## 组 131 · `0x1435E8752`

| d__ | 名字 | 状态 |
|---|---|---|
| 4 | `SolveAsync` | declared |
| 5 | `ClassifyTilesAsync` | **absent** |
| 9 | `RunAsync` | declared |

## 组 132 · `0x1435E9B02`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `StreamItem` | **absent** |
| 15 | `GetAuthorizationResponseAsync` | **absent** |
| 14 | `ListenToSingleRequestAndRespondAsync` | **absent** |

## 组 133 · `0x1435EDE5F`

| d__ | 名字 | 状态 |
|---|---|---|
| 15 | `CreateAuthenticationResultAsync` | **absent** |
| 176 | `FindRefreshTokenOrFailAsync` | **absent** |
| 14 | `RefreshRtOrFailAsync` | **absent** |
| 16 | `TryGetTokenUsingFociAsync` | **absent** |
| 5 | `ExecuteAsync` | declared |
| 10 | `GetAccountFromParamsOrLoginHintAsync` | **absent** |
| 9 | `GetSingleAccountForLoginHintAsync` | **absent** |
| 8 | `UpdateRequestWithAccountAsync` | **absent** |
| 2 | `SendAsync` | declared |
| 19 | `Poll` | declared |
| 170 | `ProcessAsync` | declared |
| 20 | `SendDeleteRequest` | **absent** |
| 0 | `SendMessages` | **absent** |
| 16 | `StartAsync` | declared |
| 23 | `DefaultWebSocketFactory` | **absent** |
| 182 | `ProcessAsync` | declared |
| 19 | `ProcessEventStream` | **absent** |
| 25 | `ProcessSocketAsync` | **absent** |
| 24 | `StartAsync` | declared |
| 26 | `StartReceiving` | **absent** |
| 27 | `StartSending` | **absent** |
| 30 | `StopAsync` | declared |

## 组 134 · `0x1435F7F2D`

| d__ | 名字 | 状态 |
|---|---|---|
| 7 | `AddImageAsync` | **absent** |
| 11 | `AddHintImageAsync` | **absent** |
| 90 | `AddHintImageAsync` | **absent** |
| 0 | `SolveFromTextAsync` | **absent** |
| 0 | `ExecuteClipModelAsync` | **absent** |
| 6 | `RunAsync` | declared |

## 组 135 · `0x1435F8CFB`

| d__ | 名字 | 状态 |
|---|---|---|
| 6 | `ElementScreenCenterAsync` | **absent** |
| 14 | `TileImageOpacityAsync` | **absent** |
| 11 | `ClickCellsAsync` | **absent** |
| 12 | `WaitTilesFadedAsync` | **absent** |
| 13 | `ReloadAsync` | declared |
| 1 | `FindSubmitButtonCoordinatesAsync` | **absent** |
| 2 | `AwaitClickProcessedAsync` | **absent** |
| 8 | `ChallengePotentiallyFailed` | **absent** |
| 3 | `ExistMoreChallenges` | **absent** |
| 56 | `FindInputFieldCoordinatesAsync` | **absent** |
| 9 | `IsChallengeSolved` | **absent** |
| 7 | `IsErrorDisplayedAsync` | **absent** |
| 0 | `WaitCaptchaResultAsync` | **absent** |
| 3 | `FindHCaptchaInformationAsync` | **absent** |
| 1 | `ReadChallengeVersion` | **absent** |
| 4 | `ReadSiteKey` | **absent** |
| 7 | `AcquireAuthorizationAsync` | **absent** |
| 10 | `InterceptAuthorizationUriAsync` | **absent** |

## 组 136 · `0x1435FC1CA`

| d__ | 名字 | 状态 |
|---|---|---|
| 16 | `DetectAsync` | declared |
| 17 | `DetectAsync` | declared |
| 0 | `SolveImageInCloudAsync` | **absent** |
| 16 | `GetChallengeRectanglesAsync` | **absent** |

