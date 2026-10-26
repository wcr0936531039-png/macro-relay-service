# 2026-10-26 A／B 驗收
A：v237 單次部署成功；來源93874fb2b5bc8a4a2c845c10bf21c8658568c7a3，保留v236回滾。
A patch SHA256：f6479e9ed71886fd3f878252db42fcb8917abb3ea5953fe02641a4e40a7fa25f
B patch SHA256：65e8150fad72099b7d3bd699bc81aa19e49d58140d2a915e58054daea7bc9ddb
dist/index.html SHA256：0e7f91e68ce7cd08a1bc143f99179f17f8218414d30342ded460ac1b829c07b2
測試：A build＋完整TZ=UTC npm test exit0；B unittest31/31、腳本20/20及相關Node全通過。
B已git am三提交；shell無push憑證，改由GitHub Git API三次同樹核對後保護性快轉main；程式頭c0c928e、資料發布a475a24。
[Actions 40316164114](https://github.com/wcr0936531039-png/macro-relay-service/actions/runs/40316164114)測試／來源核對／發布均success。
B快照：TW_M1B_M2=−0.14／2026-08／ok，IORB=2026-10-26／ok，無TW_EXPORT_ORDERS；EIA發布10/21、下次10/28，raw_thousand_barrels與page_sha256已保存。
手動巡檢03316fac-e58c-469d-a6b6-059ab9935574於2026-10-26T11:51:42.889Z完成partial；history同runId／完成時間匹配。
① PASS：本輪N=4，8299／5289／2404／5009均recorded:true，無step_timeout，history成功數4。
② FAIL：三次11:52:40Z／11:54:05Z／11:55:37Z讀回均failed、count=0、failedKinds=[all]，月報reason=CB_MONTHLY_UNAVAILABLE；登錄細項errors未由卡片API回傳，三券／目前價未驗收。
③ PASS：國發會49.68、2026-08-01、ok、scoring=pending_threshold_approval，未計分。
④ PASS：8299有「類型：各來源EPS互相分歧」，divergenceKind=sources_disagree、currentRatio=2.015487；評級仍未評，風險許可未解除。
⑤ 部分通過：最終市場／貴金屬partial29/36、refreshedThisRun=true；美股指數ok3/3，快照早於本輪，未標本輪更新。
7個信用欄過期，22:30前未重抓或改擷取時間；未將來源缺口硬改ok。
⑥ 產研PASS：半導體feed10筆，8299匹配TrendForce4筆、來源200且errors=[]；消費電子ok5筆；重大訊息六碼時間與official_key已讀回。
⑥ 分類PARTIAL：本機官方檔核對零成交26／僅量無收盤7／未列行情5；外部collector未產生notQuotedRows／missingBreakdown，站內missingBreakdown=null，巡檢缺指定新句；未補價。
⑦ PASS：WCESTUS1 validThrough=2026-10-28、releaseDateBasis=EIA頁面發布日；JPY_HV20／60採FRED官方並為ok，未走Frankfurter。
⑧ 待驗證：本輪watchlistSource=built_in_default、4檔8299／5289／2404／5009；latest_synced及私人清單一致性待擁有者開站後下一輪驗證，未冒稱已同步。
B網站已讀新中繼：M1B−M2最新重讀ok；但過期快取重讀曾變stale，SERIES75日與中繼95日時效不一致，需續修。
每日巡檢保持is_enabled=false（②未過）；已將指示固定四檔改當輪stockBatch／N，要求記錄watchlistSource，原06:30／22:30時段未變。
交接Claude：依約改用GitHub代抓可轉債；另補外部分類欄與M1B快取時效一致性。本輪未開始額外排隊功能。
憑證僅記憶體／隱藏stdin，未公開私人入口、專案代號或Tiingo原始價格。
