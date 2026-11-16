# 测试的证据来源（生成文件，勿手改）

> 由 `python analysis/test_provenance.py` 生成。判据写在脚本头里，先定后量。

## 为什么要有这份表

判据 C7c（每个函数功能相等）是 `unknown`。R719–R721 证明**从原版挑见证函数**这条路卡在元数据归属上。
那么 C7c 实际能拿出的证据量是另一个量：**有多少条断言陈述的是二进制说过的事**，
而不是把实现本身复述一遍。**1649 条全绿不等于有 1649 条证据。**

## 计数

```
测试方法总数     : 1553
binary (direct)    : 83 (5.3%)
binary (inherited) : 419 (27.0%)
neither            : 1134 (73.0%)
```

## 判据（从脚本头复制，先定后量）

一条测试算 `binary-sourced`，当且仅当方法体或紧邻的文档注释里出现：

| 标记 | 含义 |
|---|---|
| `0x14xxxxxx` | 原版镜像地址（复刻件自己的地址从不这样写） |
| `decompil` | 反编译 / Hex-Rays / 伪代码 |
| `descriptor` | 编译期 XAML 描述符表 |
| `the image` | 关于原版二进制的主张 |

**其余一律记 `implementation-derived`**，包含从文案或 UI 设计推出来的测试 ——
那些也不是从二进制推的，混进去会把这张表要报的数放大。

## 逐文件

| 文件 | direct | inherited | 总数 |
|---|---|---|---|
| `SurfaceRuntimeTests.cs` | 5 | 10 | 10 |
| `AccessorBrandCheckTests.cs` | 3 | 3 | 3 |
| `BrowserFingerprintTests.cs` | 3 | 3 | 8 |
| `DemandwareControllerTests.cs` | 3 | 7 | 7 |
| `RealmReplayTests.cs` | 3 | 3 | 8 |
| `ArrowAndBeastTests.cs` | 2 | 2 | 4 |
| `CloakRegexTests.cs` | 2 | 2 | 3 |
| `DemandwareRaffleTests.cs` | 2 | 7 | 7 |
| `EngineParityTests.cs` | 2 | 3 | 3 |
| `ForwardingShimTests.cs` | 2 | 5 | 5 |
| `GlobalSurfaceTests.cs` | 2 | 2 | 4 |
| `LiveSchemaPinsTests.cs` | 2 | 2 | 10 |
| `NoProtoMethodTests.cs` | 2 | 3 | 3 |
| `SessionTelemetryTests.cs` | 2 | 7 | 7 |
| `ShopifyCartEndpointTests.cs` | 2 | 2 | 2 |
| `ValueTailTests.cs` | 2 | 2 | 3 |
| `VisualViewportTests.cs` | 2 | 4 | 4 |
| `WallSolvingTests.cs` | 2 | 6 | 6 |
| `AccessorWordingTests.cs` | 1 | 3 | 3 |
| `AccountAndAuthFamiliesTests.cs` | 1 | 5 | 5 |
| `AntiBotProtocolTests.cs` | 1 | 5 | 5 |
| `ChromiumStealthTests.cs` | 1 | 1 | 5 |
| `CloseAndOpenFamilyTests.cs` | 1 | 1 | 7 |
| `CloudflareStrategyTests.cs` | 1 | 7 | 7 |
| `DlpaProfileTests.cs` | 1 | 1 | 7 |
| `EndpointFamilies101Tests.cs` | 1 | 1 | 5 |
| `EndpointProvenanceTests.cs` | 1 | 2 | 2 |
| `EngineAssetsTests.cs` | 1 | 1 | 7 |
| `HandlerSurfaceTests.cs` | 1 | 3 | 3 |
| `IDBEvidenceTests.cs` | 1 | 4 | 4 |
| `KasadaApiTests.cs` | 1 | 5 | 5 |
| `KasadaSolverTests.cs` | 1 | 9 | 9 |
| `KasadaStrategyTests.cs` | 1 | 7 | 7 |
| `LiveBrowserProbeTests.cs` | 1 | 1 | 1 |
| `MobileNavigatorTests.cs` | 1 | 6 | 6 |
| `NavOrderTests.cs` | 1 | 4 | 4 |
| `NavigatorLocksTests.cs` | 1 | 1 | 4 |
| `NikeCallerIdTests.cs` | 1 | 4 | 4 |
| `NikeEndpointTests.cs` | 1 | 4 | 4 |
| `NikeHeaderTests.cs` | 1 | 4 | 4 |
| `NikeMarketplaceTests.cs` | 1 | 1 | 5 |
| `NikeStepTests.cs` | 1 | 1 | 5 |
| `PageCopyTests.cs` | 1 | 16 | 16 |
| `ProfileCsvCopyTests.cs` | 1 | 1 | 4 |
| `ProfileValidationListsTests.cs` | 1 | 5 | 5 |
| `ProxyCreatorTests.cs` | 1 | 5 | 5 |
| `RetailApiFamiliesTests.cs` | 1 | 1 | 5 |
| `SessionPayloadTests.cs` | 1 | 7 | 7 |
| `ShopifyGraphQlTests.cs` | 1 | 7 | 7 |
| `ShopifyHeadersTests.cs` | 1 | 1 | 5 |
| `ShopifyHostListTests.cs` | 1 | 2 | 2 |
| `StackElisionTests.cs` | 1 | 1 | 3 |
| `StoreFlowStepsTests.cs` | 1 | 11 | 11 |
| `TaskCreatorCopyTests.cs` | 1 | 1 | 7 |
| `TasksPageTests.cs` | 1 | 1 | 12 |
| `ViewportGeometryTests.cs` | 1 | 1 | 2 |
| `WebAssemblySurfaceTests.cs` | 1 | 6 | 6 |
| `XamlBindingTableTests.cs` | 1 | 5 | 5 |
| `AccountCopyTests.cs` | 0 | 4 | 4 |
| `AccountMoveTests.cs` | 0 | 0 | 4 |
| `AccountSelectionTests.cs` | 0 | 12 | 12 |
| `AccountStoreListTests.cs` | 0 | 0 | 2 |
| `AccountTablesTests.cs` | 0 | 0 | 5 |
| `AccountsPageTests.cs` | 0 | 0 | 20 |
| `AdyenBrowserInfoTests.cs` | 0 | 0 | 5 |
| `AdyenPayPalFlowTests.cs` | 0 | 0 | 5 |
| `AllFlowsMonitorTests.cs` | 0 | 0 | 2 |
| `AnalyticsAndModalTests.cs` | 0 | 0 | 8 |
| `AntiBotVendorTests.cs` | 0 | 5 | 5 |
| `AppVersionTests.cs` | 0 | 0 | 2 |
| `BackfillTests.cs` | 0 | 0 | 18 |
| `BackupSchedulerTests.cs` | 0 | 0 | 5 |
| `BindDiffGuardTests.cs` | 0 | 0 | 3 |
| `BindScopeGuardTests.cs` | 0 | 0 | 2 |
| `BindingGapRatchetTests.cs` | 0 | 0 | 3 |
| `BouncyTlsTests.cs` | 0 | 0 | 5 |
| `BrotliDictionaryTests.cs` | 0 | 0 | 4 |
| `BrowserIdentityTests.cs` | 0 | 0 | 5 |
| `CandidateStepTests.cs` | 0 | 0 | 5 |
| `CandidateStepsDigestTests.cs` | 0 | 3 | 3 |
| `CanvasSurfaceTests.cs` | 0 | 0 | 4 |
| `CasioEndpointTests.cs` | 0 | 0 | 1 |
| `CatalogSelfDomainTests.cs` | 0 | 0 | 3 |
| `CatalogValidatorTests.cs` | 0 | 0 | 4 |
| `ChartTimelineTests.cs` | 0 | 0 | 6 |
| `CheckboxLabelTests.cs` | 0 | 0 | 2 |
| `CheckoutFailureModeTests.cs` | 0 | 0 | 7 |
| `CheckoutFlowEndToEndTests.cs` | 0 | 0 | 6 |
| `CheckoutFormBuilderTests.cs` | 0 | 0 | 8 |
| `CheckoutHistoryShapeTests.cs` | 0 | 0 | 2 |
| `CheckoutHistoryTests.cs` | 0 | 0 | 4 |
| `CheckoutStatsTests.cs` | 0 | 0 | 5 |
| `ChildRealmParityTests.cs` | 0 | 0 | 2 |
| `ChromiumBridgeTests.cs` | 0 | 0 | 4 |
| `CloneNamingTests.cs` | 0 | 0 | 3 |
| `CloudflareClearanceTests.cs` | 0 | 0 | 5 |
| `ComboBoxEditTests.cs` | 0 | 5 | 5 |
| `ConcurrencyGateTests.cs` | 0 | 0 | 5 |
| `ControllerCensusTests.cs` | 0 | 0 | 4 |
| `CookieEvidenceRatchetTests.cs` | 0 | 2 | 2 |
| `CopyAuditConsistencyTests.cs` | 0 | 0 | 1 |
| `CopyTablesHygieneTests.cs` | 0 | 3 | 3 |
| `CopyUrlTests.cs` | 0 | 0 | 3 |
| `CoreTests.cs` | 0 | 0 | 11 |
| `CssStylePropertiesTests.cs` | 0 | 0 | 2 |
| `CustomBrowserTests.cs` | 0 | 0 | 5 |
| `CustomPresetsTests.cs` | 0 | 0 | 4 |
| `CustomSizesPageTests.cs` | 0 | 0 | 5 |
| `CustomStoreRegistrationTests.cs` | 0 | 0 | 7 |
| `CustomStoresPageTests.cs` | 0 | 0 | 5 |
| `CustomStoresRowsTests.cs` | 0 | 2 | 2 |
| `CybersoleHostTests.cs` | 0 | 6 | 6 |
| `DataExportCopyTests.cs` | 0 | 1 | 1 |
| `DeadButtonTests.cs` | 0 | 0 | 2 |
| `DeclaredStyleAccessorTests.cs` | 0 | 0 | 2 |
| `DecompilationDerivedValidationProbes.cs` | 0 | 7 | 7 |
| `DemandwareAndFootsitesTests.cs` | 0 | 0 | 2 |
| `DemandwareDualPathTests.cs` | 0 | 5 | 5 |
| `DemandwareStepMapTests.cs` | 0 | 0 | 6 |
| `DeviceTableTests.cs` | 0 | 0 | 9 |
| `DialogFieldTests.cs` | 0 | 2 | 2 |
| `DocsConsistencyTests.cs` | 0 | 0 | 7 |
| `DomainClaimTests.cs` | 0 | 0 | 3 |
| `EmptyViewTests.cs` | 0 | 0 | 5 |
| `EndpointEvidenceRatchetTests.cs` | 0 | 3 | 3 |
| `EndpointLedgerTests.cs` | 0 | 0 | 3 |
| `ErrorCatalogDigestTests.cs` | 0 | 3 | 3 |
| `ErrorCatalogTests.cs` | 0 | 0 | 6 |
| `EventBusLimitsTests.cs` | 0 | 0 | 5 |
| `ExportServiceTests.cs` | 0 | 0 | 5 |
| `FingerprintLayersTests.cs` | 0 | 0 | 6 |
| `FirstDomainResolvesTests.cs` | 0 | 0 | 2 |
| `FlowArtifactTests.cs` | 0 | 0 | 3 |
| `FlowCatalogTests.cs` | 0 | 0 | 8 |
| `FontMediaSurfaceTests.cs` | 0 | 0 | 4 |
| `GeneralSettingsLayoutTests.cs` | 0 | 0 | 4 |
| `GeometryLedgerTests.cs` | 0 | 0 | 3 |
| `GlobalPruneTests.cs` | 0 | 0 | 4 |
| `GoatAccountSurfaceTests.cs` | 0 | 4 | 4 |
| `GoogleOAuthFlowTests.cs` | 0 | 0 | 4 |
| `GraphQlCartStepTests.cs` | 0 | 0 | 5 |
| `GreaseTests.cs` | 0 | 0 | 8 |
| `GroupBindingAndReasonsTests.cs` | 0 | 0 | 5 |
| `GroupCounterTests.cs` | 0 | 0 | 6 |
| `GroupGridTests.cs` | 0 | 0 | 6 |
| `GroupSummaryTests.cs` | 0 | 4 | 4 |
| `HbxPlatformTests.cs` | 0 | 0 | 1 |
| `HelpPageTests.cs` | 0 | 0 | 4 |
| `HelpViewTests.cs` | 0 | 2 | 2 |
| `HomePageParityTests.cs` | 0 | 0 | 6 |
| `HomeSplitTests.cs` | 0 | 0 | 2 |
| `HpackHuffmanTests.cs` | 0 | 0 | 4 |
| `Http2Tests.cs` | 0 | 0 | 12 |
| `HttpAnalyticsFlushTests.cs` | 0 | 0 | 4 |
| `HybrisCartPathTests.cs` | 0 | 0 | 1 |
| `IWebhookContractTests.cs` | 0 | 3 | 3 |
| `IdentifierFieldProbeTests.cs` | 0 | 0 | 1 |
| `ImportParserTests.cs` | 0 | 0 | 7 |
| `InterfaceInventoryTests.cs` | 0 | 0 | 1 |
| `Ja3Tests.cs` | 0 | 0 | 6 |
| `JbHiFiPlatformTests.cs` | 0 | 0 | 1 |
| `JohnLewisPriceTests.cs` | 0 | 0 | 4 |
| `JohnLewisStepMapTests.cs` | 0 | 0 | 6 |
| `JsGuardTests.cs` | 0 | 0 | 4 |
| `JsParseTests.cs` | 0 | 0 | 2 |
| `JsonFileStoreLockTests.cs` | 0 | 0 | 3 |
| `KasadaHeaderSurfaceTests.cs` | 0 | 0 | 4 |
| `KasadaIdentityChainTests.cs` | 0 | 0 | 4 |
| `KasadaIdentityPinTests.cs` | 0 | 0 | 6 |
| `KasadaIntrospectionTests.cs` | 0 | 0 | 4 |
| `KasadaLiveTests.cs` | 0 | 0 | 2 |
| `KasadaRealScriptTests.cs` | 0 | 0 | 7 |
| `KeyBindChordTests.cs` | 0 | 0 | 3 |
| `KeyBindMatcherTests.cs` | 0 | 0 | 11 |
| `KeyBindsPageTests.cs` | 0 | 0 | 6 |
| `KeyOrderDispatchTests.cs` | 0 | 0 | 3 |
| `KeyOrderTableTests.cs` | 0 | 0 | 3 |
| `LambdaWitnessTests.cs` | 0 | 0 | 6 |
| `LinkFilterTests.cs` | 0 | 0 | 4 |
| `ListPageColumnsTests.cs` | 0 | 0 | 3 |
| `LiveContractTests.cs` | 0 | 0 | 9 |
| `LiveTlsTests.cs` | 0 | 0 | 1 |
| `LocaleDictionaryTests.cs` | 0 | 0 | 7 |
| `LoginControlTests.cs` | 0 | 0 | 4 |
| `MagentoWrappingTests.cs` | 0 | 0 | 1 |
| `MailAndCaptchaTests.cs` | 0 | 0 | 20 |
| `MainWindowCommandTests.cs` | 0 | 0 | 3 |
| `MaskTargetsTests.cs` | 0 | 0 | 4 |
| `MediaQuerySurfaceTests.cs` | 0 | 0 | 3 |
| `MethodPatchTableTests.cs` | 0 | 0 | 4 |
| `MetricClaimsTests.cs` | 0 | 0 | 3 |
| `MobileSurfaceTests.cs` | 0 | 7 | 7 |
| `ModuleCoverageTests.cs` | 0 | 0 | 4 |
| `ModuleReachabilityTests.cs` | 0 | 0 | 1 |
| `ModuleRobustnessTests.cs` | 0 | 0 | 5 |
| `MonitorFilterTests.cs` | 0 | 0 | 5 |
| `MonitorViewBehaviourPins.cs` | 0 | 0 | 3 |
| `MonitorViewCommandTests.cs` | 0 | 9 | 9 |
| `MoveDialogCaptionTests.cs` | 0 | 0 | 2 |
| `MultiProductTaskTests.cs` | 0 | 0 | 4 |
| `NativeArityTests.cs` | 0 | 4 | 4 |
| `NativeMaskTests.cs` | 0 | 5 | 5 |
| `NavPruneTests.cs` | 0 | 5 | 5 |
| `NavigatorCensusTests.cs` | 0 | 0 | 5 |
| `NavigatorPlacementTests.cs` | 0 | 0 | 4 |
| `NetClientLoopbackProbeTests.cs` | 0 | 0 | 1 |
| `NetworkRecorderLiveTests.cs` | 0 | 0 | 2 |
| `NetworkRecorderTests.cs` | 0 | 0 | 4 |
| `NikeKasadaFlowTests.cs` | 0 | 0 | 3 |
| `NonParityClaimsTests.cs` | 0 | 0 | 6 |
| `NotificationPopupTests.cs` | 0 | 0 | 1 |
| `NotificationsPageTests.cs` | 0 | 0 | 6 |
| `OffspringPlatformTests.cs` | 0 | 0 | 1 |
| `OriginalViewClassParityTests.cs` | 0 | 0 | 5 |
| `OwnTlsFallbackTests.cs` | 0 | 0 | 4 |
| `PageKeyProbeTests.cs` | 0 | 0 | 1 |
| `ParityDocTests.cs` | 0 | 0 | 9 |
| `PatchJournalTests.cs` | 0 | 3 | 3 |
| `PayloadCoverageTests.cs` | 0 | 0 | 5 |
| `PaymentPageTests.cs` | 0 | 0 | 4 |
| `PaymentViewTests.cs` | 0 | 0 | 2 |
| `PerformanceTests.cs` | 0 | 0 | 2 |
| `PlatformAssignmentTests.cs` | 0 | 0 | 11 |
| `PlatformEvidenceTests.cs` | 0 | 0 | 1 |
| `PlatformTableTests.cs` | 0 | 0 | 2 |
| `PollingSolverTests.cs` | 0 | 6 | 6 |
| `PopMartCartWiringTests.cs` | 0 | 0 | 5 |
| `PopMartEndpointTests.cs` | 0 | 5 | 5 |
| `PopMartPriceTests.cs` | 0 | 0 | 6 |
| `PopMartStepMapTests.cs` | 0 | 5 | 5 |
| `ProductPageProbeTests.cs` | 0 | 0 | 2 |
| `ProfileAllocationTests.cs` | 0 | 0 | 7 |
| `ProfileCloneTests.cs` | 0 | 0 | 5 |
| `ProfileCsvParseTests.cs` | 0 | 0 | 3 |
| `ProfileCsvRowTests.cs` | 0 | 5 | 5 |
| `ProfileMoveTests.cs` | 0 | 0 | 3 |
| `ProfilePanelTests.cs` | 0 | 0 | 2 |
| `ProfileProxyBindingTests.cs` | 0 | 0 | 3 |
| `ProviderFetchBalanceTests.cs` | 0 | 0 | 2 |
| `ProxiesPageTests.cs` | 0 | 0 | 14 |
| `ProxyClearTests.cs` | 0 | 0 | 4 |
| `ProxyCloneMoveTests.cs` | 0 | 0 | 4 |
| `ProxyRotatorTests.cs` | 0 | 0 | 8 |
| `ProxyRowTestTests.cs` | 0 | 0 | 2 |
| `ProxySiteTestTests.cs` | 0 | 0 | 3 |
| `ProxyTableTests.cs` | 0 | 0 | 4 |
| `PruneWhitelistTests.cs` | 0 | 5 | 5 |
| `QueryParamEvidenceRatchetTests.cs` | 0 | 2 | 2 |
| `RailWidthTests.cs` | 0 | 0 | 3 |
| `RealPageParserTests.cs` | 0 | 0 | 2 |
| `RenderedProxyTableTests.cs` | 0 | 0 | 5 |
| `ScapiAppPathTests.cs` | 0 | 5 | 5 |
| `ServiceHostTests.cs` | 0 | 10 | 10 |
| `ServiceRoadPollingTests.cs` | 0 | 5 | 5 |
| `SessionPayloadBuilderTests.cs` | 0 | 7 | 7 |
| `SessionSinkWiringTests.cs` | 0 | 0 | 7 |
| `SettingsDialogSingleSourceTests.cs` | 0 | 0 | 4 |
| `SettingsModalTests.cs` | 0 | 0 | 8 |
| `SettingsNavTests.cs` | 0 | 2 | 2 |
| `SettingsPageHeadersTests.cs` | 0 | 0 | 5 |
| `SettingsPagesTests.cs` | 0 | 0 | 4 |
| `SettingsShellTests.cs` | 0 | 0 | 13 |
| `SettingsStorageLinkTests.cs` | 0 | 0 | 5 |
| `ShapeAuditGuardTests.cs` | 0 | 0 | 2 |
| `ShippingRateSelectionTests.cs` | 0 | 0 | 7 |
| `ShopifyWrappingTests.cs` | 0 | 0 | 2 |
| `SizeFieldProbeTests.cs` | 0 | 0 | 1 |
| `SizePaletteTests.cs` | 0 | 0 | 8 |
| `SmartActionRowTests.cs` | 0 | 6 | 6 |
| `SmartActionTests.cs` | 0 | 0 | 6 |
| `SmartActionViewTests.cs` | 0 | 0 | 15 |
| `SmartActionWindowOpsTests.cs` | 0 | 0 | 1 |
| `SoundPlayerTests.cs` | 0 | 0 | 3 |
| `SourceEncodingTests.cs` | 0 | 0 | 2 |
| `SplashWindowTests.cs` | 0 | 3 | 3 |
| `StatusOverwriteTests.cs` | 0 | 0 | 3 |
| `StepActionTests.cs` | 0 | 0 | 18 |
| `StoreApiFamiliesTests.cs` | 0 | 0 | 5 |
| `StoreFlowDigestTests.cs` | 0 | 2 | 2 |
| `StoreFlowParityTests.cs` | 0 | 0 | 15 |
| `StoreFlowSourceTests.cs` | 0 | 0 | 2 |
| `StoreRegistryResolveTests.cs` | 0 | 0 | 7 |
| `SummaryBlockTests.cs` | 0 | 0 | 4 |
| `SupremePlatformTests.cs` | 0 | 0 | 1 |
| `SurfaceInjectionTests.cs` | 0 | 5 | 5 |
| `SurfaceOrderTests.cs` | 0 | 0 | 5 |
| `TaskClipboardActionTests.cs` | 0 | 4 | 4 |
| `TaskCloneTests.cs` | 0 | 0 | 4 |
| `TaskEngineIntegrationTests.cs` | 0 | 0 | 7 |
| `TaskGridColumnTests.cs` | 0 | 0 | 2 |
| `TaskGroupOrderingTests.cs` | 0 | 0 | 5 |
| `TaskGroupSyncTests.cs` | 0 | 0 | 6 |
| `TaskGroupViewTests.cs` | 0 | 3 | 3 |
| `TaskMoveTests.cs` | 0 | 0 | 4 |
| `TaskPolicyTests.cs` | 0 | 0 | 6 |
| `TaskProfileViewTests.cs` | 0 | 0 | 22 |
| `TaskViewCommandTests.cs` | 0 | 0 | 3 |
| `ThreeDSAutoOpenPolicyTests.cs` | 0 | 0 | 6 |
| `Tls12HandshakeTests.cs` | 0 | 0 | 4 |
| `Tls12PoolTests.cs` | 0 | 0 | 5 |
| `Tls12PrfTests.cs` | 0 | 0 | 8 |
| `TlsTests.cs` | 0 | 0 | 6 |
| `TlsTransportPerformanceTests.cs` | 0 | 0 | 3 |
| `TrafficCountingStreamTests.cs` | 0 | 0 | 5 |
| `TransportParityProbeTests.cs` | 0 | 0 | 1 |
| `TypePresenceTriageTests.cs` | 0 | 0 | 1 |
| `UiContinuationTests.cs` | 0 | 0 | 1 |
| `UnassignedFieldGuardTests.cs` | 0 | 0 | 3 |
| `UnreachedUiTypesTests.cs` | 0 | 0 | 3 |
| `UnsubscribedEventsTests.cs` | 0 | 0 | 1 |
| `UserAgentConsistencyTests.cs` | 0 | 0 | 4 |
| `UtilitiesAndProbeTests.cs` | 0 | 0 | 5 |
| `VendorWiringTests.cs` | 0 | 0 | 7 |
| `VerifyRetryPolicyTests.cs` | 0 | 0 | 6 |
| `VerifyStepsTests.cs` | 0 | 0 | 4 |
| `VoiceListTests.cs` | 0 | 0 | 2 |
| `WallDispatchTests.cs` | 0 | 0 | 5 |
| `WarhammerEndpointTests.cs` | 0 | 0 | 2 |
| `WarhammerHostTests.cs` | 0 | 0 | 1 |
| `WebGlSurfaceTests.cs` | 0 | 0 | 3 |
| `WebhookCreatorLabelTests.cs` | 0 | 0 | 2 |
| `WebhookExtraFieldsTests.cs` | 0 | 2 | 2 |
| `WindowBaselineTests.cs` | 0 | 0 | 2 |
| `WindowGeometryTests.cs` | 0 | 3 | 3 |
| `WindowNameTableTests.cs` | 0 | 0 | 3 |
| `WindowNamesInstalledTests.cs` | 0 | 0 | 2 |
| `WindowOrderFidelityTests.cs` | 0 | 0 | 2 |
| `WindowOrderTests.cs` | 0 | 0 | 2 |
| `WindowOrderWrapTests.cs` | 0 | 0 | 3 |

## 局限（必须读）

**标记法不等于溯源法。** 一条测试带了 `0x14` 地址，不代表它的期望值真的从那个地址推出来；
反过来，一条没有标记的测试也可能间接依赖反编译结论（例如它测的函数是根据反编译写的）。
这张表量的是**显式可追溯性**，不是真实来源。
**所以它是下界**：真正从二进制来的测试**不少于**这个数，但不会多于总数。
