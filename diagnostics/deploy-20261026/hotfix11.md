# hotfix11｜2026-11-06 12:20 完成部署與既有資料讀回
- 擁有者已在本對話授權；三包SHA全符：relay2=3767e66c69c1062e28002fa6638c9718ec7656333756c56938b0fd2edeb83011、v253=89d4971f4c192746178ffb78154968e83369084569570d6d8582e0bc1b5b4e50、v254=9f5da93cb360a3cd78d72a29e35c6bfb1bd0d72be77801590885e6acdbabea98。
- 中繼git am成功、47/47過；CLI缺登入，改GitHub連接器非強推main commit e8b375999c2d5c2972681110a5171fa2617f792e，發布樹e3d8b0453c238a5bd0e7083d6f210c2a6b6629cc與本機完全相同（含執行權限）。
- 網站a09fea9基線→v253→v254→build→完整TZ=UTC npm test exit0（末組89/89、fail0）；來源3785fe00941ef540120cb3dcfb94aa0eae114ca1單次部署succeeded，Sites原生250＝功能v253＋v254，原生249留回滾；私人存取與RELAY_OFFICIAL_IMPORT_ENABLED=true保留。
- 正式首頁HTTP200、HTML de5a6d6bd6b55b777985fb05b50b455b0db7c6ec8b4c476a6e8905211da37deb；匿名化後台99f2ce82f426493402e5bd6784f989e6f2396d022d9c9aa7113e1ef22abf5944相符，實際後台fd396541da546ee14e8579c5110a4d9bd22e73b52161a2e8ab603846e748d208；未公開私人字串。
- 信用7/7讀回欄位通過：融資金額／增減／張數、融券張數／增減、市值比、信用成交值均date=11/04、previousDate=11/03、previousDateBasis=official_trading_calendar；capturedAt=2026-11-05T01:51:37.817366+00:00、capturedAtBasis=external_collector_capture、captureDeferred=false。
- 上列是既有匯入資料經新程式重讀的保存快照（checkedAt台北11/06 07:31；12:18 GET200、refreshing=true），不是新信用匯入；下一次合規新匯入驗收仍未完成，未將上午05:26新信用匯入來湊驗收。
- 排程比對：11/05 22:30平台六秒failed無錯誤本文，不能證實是審查／額度；23:02另一輪工具確實Automatic approval review failed／usage limit；手動22:41正常，11/06晨間平台completed且同run Gate5/5。不同事件分開記錄。
- prompt已補明10/26 21:25擁有者對日常POST及GET status/history的授權並讀回一致；06:30／22:30與enabled=true未改，授權文字不能解除額度限制。既有巡檢另存一次性v254合規新匯入七列驗收，完成後補本檔並標記；不建立新任務。
- 未另改程式：中繼auto上午仍收信用、21:00起即照收的時段治理缺口未在兩包內，保持待修；詳見diagnostics/automation-runs/20261106-morning.md。
