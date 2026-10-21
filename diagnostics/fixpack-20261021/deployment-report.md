# 2026-10-21 修正包＋C2 部署 v231：正式驗收紀錄

已獲擁有者直接授權，部署 succeeded；保留 v230 回滾。僅包含核准修正包及 C2。整站巡檢仍為 partial，不能把部署成功寫成所有研究／資料缺口均已解決。

## 來源、順序與完整測試

乾淨原站基線 `f9c5f15b371de58d0a06ef5251ce5c8a895f217e` → fixpack.patch → node build.mjs → c2.patch → node build.mjs。無衝突。部署來源 commit `6b924076503a47e346a3d72ff3efeb5260a8078f`。部署前再跑完整 npm test，exit 0；全部 legacy、NYSE calendar 9 項、advisory integration 38 項、fixpack 4 項、C2 5 項通過，fail 0。git diff --check 通過。

|項目|SHA-256|
|---|---|
|fixpack.patch|d69ac5bb2538c9b3115306eb8c490077797b284a69e9c07151dbcf560bae6d0c|
|c2.patch|9ad8c47bae31fa31008f88895b8a40e3f46fbf9ec6d94f505c6215dd69ad34e4|
|HTML／正式首頁讀回|93d22d219109e52161e0e85ab926ad86dab6fadfc5083c57144e5c21b1f9e638|
|Worker／上傳包內 Worker|613ac53005c0346259bf4aff78f95e18ced8c4c29a81f1d964ff9b4a56e79675|
|上傳前 tar.gz 檔案|6677b25e83c5cb3cc1bd3219d6b311c3ab1d318b9b6a6e937fbe6025cdaeb48e|
|平台保存的 archive content_hash|d10b2337951fb829850232a8da31943256a5c05486285e5d0f8319dee0628831|

最後兩列是各自儲存層的封裝雜湊，不將平台重封裝 tar 與本機 gzip 視為同一位元組檔案。已直接查核本機上傳包內 HTML／Worker 均為核准雜湊；平台版本來源 commit 亦相符。

完整讀回摘要：[deployment-readback.json](deployment-readback.json)。完整原始碼 diff：[fixpack.patch](fixpack.patch)、[c2.patch](../c2-20261021/c2.patch)。兩份為已審 source patch；生成 Worker 由 build 重建，避免再次公開編譯上下文中的私人操作說明。完整本輪測試：[deployment-npm-test.log](deployment-npm-test.log)。

## 正式 API 讀回

|目錄|部署前實際列／不同 id|部署後列／不同 id|部署後有效覆蓋|
|---|---:|---:|---:|
|核心總經|65/55|55/55|55/55|
|市場／貴金屬|36/36|36/36|36/36|
|擴展總經|12/12|12/12|12/12（巡檢讀回）|

核心固定55個不同指標，原65列有10個重複id；市場固定36，擴展12另列。缺項保留不消失的空資料、缺值、去重情境已在修正包測試驗證，未用重複列提高覆蓋率。

### B1 真實單日讀回

|指標|部署前變化／比較起日|部署後變化／比較起日|部署後觀測日|
|---|---|---|---|
|SP500|-1.49233276%／2026-10-12|0.28397824%／2026-10-19|2026-10-20|
|DJIA|0.22271702%／2026-10-12|1.01960839%／2026-10-19|2026-10-20|
|NASDAQCOM|-2.99131245%／2026-10-12|-0.02296555%／2026-10-19|2026-10-20|
|DCOILWTICO|7.25110503%／2026-10-07|1.04104700%／2026-10-13|2026-10-14|
|DCOILBRENTEU|0.43650794%／2026-10-07|0.61218000%／2026-10-13|2026-10-14|
|DHHNGSP|1.89873418%／2026-10-07|2.54777070%／2026-10-13|2026-10-14|
|TWSE_TAIEX|-1.13000000%／原列未提供|-1.13000000%／原列未提供|2026-10-20|
|TWSE_ELECTRONIC|-0.92000000%／原列未提供|-0.92000000%／原列未提供|2026-10-20|
|TWSE_SEMICONDUCTOR|-0.94000000%／原列未提供|-0.94000000%／原列未提供|2026-10-20|
|TWSE_FINANCIAL|-2.36000000%／原列未提供|-2.36000000%／原列未提供|2026-10-20|
|TWSE_SHIPPING|-1%／原列未提供|-1%／原列未提供|2026-10-20|
|TWSE_STEEL|-0.51000000%／原列未提供|-0.51000000%／原列未提供|2026-10-20|

部署前有重複id時取末列，與畫面及後台Map一致；TWSE直接公布官方單日變化，原列未提供previousDate時照實留缺，沒有補造起日。部署前後來源可能已發布新交易日，表中保留兩端實際觀測日；不把10/19與10/20當成同一輸入。凍結同資料驗收另已核對SP500 10/19 +0.408516%、WTI 10/14 +1.041047%、HenryHub 10/14 +2.547771%。本輪正式總經主API股指已前進到10/20。

獨立股指API曾命中部署前04:56建立的15分鐘持久快取。未改原始碼或手改快取時間，等原TTL自然到期後再讀，背景更新完成；最終3/3均為相鄰觀測，舊5筆變化已消失。

|獨立股指|觀測日|比較起日|單日變化|
|---|---|---|---:|
|SP500|2026-10-20|2026-10-19|0.28397824%|
|DJIA|2026-10-20|2026-10-19|1.01960839%|
|NASDAQCOM|2026-10-20|2026-10-19|-0.02296555%|

### 總經分數

|市場|部署前本輪讀回|部署後本輪讀回|
|---|---:|---:|
|US|59|64|
|TW|58|60|

即時數據與上次凍結驗收不同：美股動能45→62.5；成長／就業75→72；台股本土41→49.375。源於單日修正與官方資料更新，沒有改公式、權重或門檻。同一凍結輸入的原核准結果US59→65、TW58→59另保留，不能硬套成即時分數。C2本身不改總經分數。

### 融資／融券最終值與保存

官方10/20報表於 2026-10-21T04:56:58.257078+00:00 重抓，第一次嘗試成功。匯入回應及獨立official-import-status讀回相符：8個原始欄位、previousFinalDate=2026-10-19、revisionCount=9。9筆包括首次建立final/provisional及衍生點，不能說9個舊值全部被更正。市場API歷史再讀回：

|觀測日|融資（億元）|融券（張）|性質|公布報表日期|
|---|---:|---:|---|---|
|2026-10-19|6406.17928|201911|final|2026-10-20|
|2026-10-20|6381.00111|215912|provisional|2026-10-20|

原10/19報表暫定640618432仟元，翌日公布前日640617928仟元，差−504仟元；本輪正式book首次初始化，沒有偽造舊book的before。10/19缺已保存同日市值分母時，不造10/19融資占比；10/20採同日市值。當日餘額列仍標暫定，沒有把隔日最終值套在錯誤日期。

D1表格檢視器循回傳next_offset翻至大型cache列時拒絕顯示單列（A single D1 row is too large to display safely）；未繞過限制或宣稱直接讀到完整revision book。驗證證據為匯入後狀態讀回與市場API的final歷史點；後續隔日更新仍須持續觀察。

## 四檔 Master、Gate 與風險限制

|股票|正式讀回|EPS最大／最小|風險許可|
|---|---|---:|---|
|8299|未評（估值分歧）|10.69153846|not_cleared|
|5289|未評（估值分歧）|14.63234871|not_cleared|
|2404|未評（估值分歧）|3.11795113|not_cleared|
|5009|C／保守觀察|1.51713919|not_cleared|

群聯39／206.883／220.20／416.97→10.69153846倍。三檔分歧均不給D或其他貴便宜等級；5009維持C。下次財報為2026Q3法定期限11/14，已標法定期限，不是假稱公司公告日期。

第一輪部署前與部署後曾有過期快照、群聯FinMind402，保留失敗紀錄。使用既有refresh端點一次重試後，群聯checkedAt=2026-10-21T05:06:18.128Z並恢復有效計算；沒有回填舊資料或放寬條件。其他三檔在全站刷新後也解除先前過期狀態。

### 同一輸入的程式前後比較

另把本輪新抓的相同股票、總經、市場、擴展、全市場掃描、公司／合格共識輸入，同時餵給v230與v231：40個Gate狀態0變化，scoring及VETO物件四檔完全相同；風險許可四檔均not_cleared。三檔D→未評、5009 C→C，是C2唯一指定的評級變化。這是同資料控制組，不把實際刷新造成的變化掩蓋掉。證據：[identical-live-inputs-comparison.json](identical-live-inputs-comparison.json)。

### 實際時間前後的每個 Gate

下表如實顯示部署前過期資料→部署後重新抓取資料的差異，不能宣稱實際前後40格完全相同。變化原因為恢復有效資料；Gate判定程式在相同輸入控制組不變。

|股票|Gate|前|後|
|---|---:|---|---|
|8299|1|partial|evaluated|
|8299|2|evaluated|evaluated|
|8299|3|evaluated|evaluated|
|8299|4|warning|warning|
|8299|5|partial|partial|
|8299|6|partial|warning|
|8299|7|blocked|evaluated|
|8299|8|partial|partial|
|8299|9|blocked|conditional|
|8299|10|blocked|evaluated|
|5289|1|partial|evaluated|
|5289|2|evaluated|evaluated|
|5289|3|evaluated|evaluated|
|5289|4|blocked|warning|
|5289|5|needs_user_records|needs_user_records|
|5289|6|blocked|warning|
|5289|7|blocked|evaluated|
|5289|8|needs_user_records|needs_user_records|
|5289|9|blocked|blocked|
|5289|10|blocked|evaluated|
|2404|1|partial|evaluated|
|2404|2|evaluated|evaluated|
|2404|3|evaluated|evaluated|
|2404|4|blocked|partial|
|2404|5|needs_user_records|needs_user_records|
|2404|6|blocked|partial|
|2404|7|blocked|evaluated|
|2404|8|needs_user_records|needs_user_records|
|2404|9|blocked|partial|
|2404|10|blocked|evaluated|
|5009|1|partial|evaluated|
|5009|2|evaluated|evaluated|
|5009|3|evaluated|evaluated|
|5009|4|blocked|warning|
|5009|5|needs_user_records|needs_user_records|
|5009|6|blocked|warning|
|5009|7|blocked|evaluated|
|5009|8|needs_user_records|needs_user_records|
|5009|9|blocked|conditional|
|5009|10|blocked|evaluated|

群聯Gate6 CFO／淨利−0.17倍、FCF−141.57億元持續警示；5289及5009現金流警訊保留。Gate5A/5B及Gate8缺合格樣本／直接同業等限制未解除。VETO仍pending、每檔仍有4條未知；刷新後的已核實條件才恢復clear，不因C2分歧解除未知否決或風險預算。

## B2、巡檢保存及其他觀察

- 早晚標示06:30／22:30、來源provider、Tiingo主要／Yahoo備援文字、核心／擴展分母、後台4檔與私人追蹤範圍、金銀同一報價bundle、最低級與均線範圍等7項，皆為已核准原始碼；原全套相關測試通過。
- 金銀卡片經同一coherentMetalRows讀比值operands；無新的貴金屬計分、無改五維權重。
- 服務存取沒有簽入私人訪客身分；未冒用擁有者header讀私人清單，也未將後台4檔當成私人5檔全數完成。
- 全站run `0bacb91f-9834-4bcf-9eef-bdfc6a9872b7` 於 2026-10-21T05:01:56.696Z 完成partial，匹配runId歷史已保存。總經55/55、擴展12/12、市場36/36、股指3/3、跨市場4/4、公告3/3。
- 該run板塊模組逾時；後續獨立API讀回OK，Tiingo主要來源adjClose、觀測10/20、11/11，新增貢獻仍0。未倒改原run的partial或說成整站全數完成。
- 本輪檢查正式API、實際HTML雜湊及程式／資料控制組；未把這些結果當成擁有者登入瀏覽器的人工視覺驗收。
- 部署後錯誤篩選日誌未發現未處理Worker exception；有受保護路由401、登入／favicon404與取消請求。API及首頁讀回正常，未觸發整體故障回滾，v230仍保留。
- 不新增回測因子、不啟用加減分／持股換算表、不擴大至C1/C3/C4或其他待辦。Tiingo原始價格、憑證、私人網站入口及專案識別資訊未寫入公開紀錄。

## 所有來源列的 status／is_stale／reason 變化

包含總經、市場、擴展與獨立股指；只列這三個欄位確有改變的列。值、日期、單日欄位等完整前後差異另存 [deployment-live-comparison.json](deployment-live-comparison.json)。

|範圍／指標|欄位|前|後|
|---|---|---|---|
|macro/TWSE_TOTAL_TRADE_VALUE|reason|null|null|
|macro/TWSE_MARGIN_BALANCE_NTD|reason|null|null|
|macro/TWSE_MARGIN_CHANGE_NTD|reason|null|null|
|macro/TWSE_MARGIN_BALANCE_UNITS|reason|null|null|
|macro/TWSE_SHORT_BALANCE|reason|null|null|
|macro/TWSE_SHORT_CHANGE|reason|null|null|
|macro/TWSE_MARGIN_MARKET_CAP_RATIO|reason|null|null|
|macro/TWSE_CREDIT_TRADE_VALUE|reason|null|null|
|market/TWSE_TOTAL_TRADE_VALUE|reason|null|null|
|market/TWSE_MARGIN_BALANCE_NTD|reason|null|null|
|market/TWSE_MARGIN_CHANGE_NTD|reason|null|null|
|market/TWSE_MARGIN_BALANCE_UNITS|reason|null|null|
|market/TWSE_SHORT_BALANCE|reason|null|null|
|market/TWSE_SHORT_CHANGE|reason|null|null|
|market/TWSE_MARGIN_MARKET_CAP_RATIO|reason|null|null|
|market/TWSE_CREDIT_TRADE_VALUE|reason|null|null|
|expanded/PAYEMS|status|stale|ok|
|expanded/PAYEMS|is_stale|true|false|
|expanded/PAYEMS|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/UNRATE|status|stale|ok|
|expanded/UNRATE|is_stale|true|false|
|expanded/UNRATE|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/SAHMREALTIME|status|stale|ok|
|expanded/SAHMREALTIME|is_stale|true|false|
|expanded/SAHMREALTIME|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/RSAFS|status|stale|ok|
|expanded/RSAFS|is_stale|true|false|
|expanded/RSAFS|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/NOCDFSA066MSFRBPHI|status|stale|ok|
|expanded/NOCDFSA066MSFRBPHI|is_stale|true|false|
|expanded/NOCDFSA066MSFRBPHI|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/NYFED_EMPIRE_ORDERS|status|stale|ok|
|expanded/NYFED_EMPIRE_ORDERS|is_stale|true|false|
|expanded/NYFED_EMPIRE_ORDERS|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/DALLAS_TMOS_ORDERS|status|stale|ok|
|expanded/DALLAS_TMOS_ORDERS|is_stale|true|false|
|expanded/DALLAS_TMOS_ORDERS|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/GDPNOW|status|stale|ok|
|expanded/GDPNOW|is_stale|true|null|
|expanded/GDPNOW|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/BAMLH0A0HYM2|status|stale|ok|
|expanded/BAMLH0A0HYM2|is_stale|true|false|
|expanded/BAMLH0A0HYM2|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/TW_EXPORT_ORDERS|status|stale|ok|
|expanded/TW_EXPORT_ORDERS|is_stale|true|false|
|expanded/TW_EXPORT_ORDERS|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/TW_NDC_SIGNAL|status|stale|ok|
|expanded/TW_NDC_SIGNAL|is_stale|true|false|
|expanded/TW_NDC_SIGNAL|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|expanded/TW_M1B_M2|status|stale|ok|
|expanded/TW_M1B_M2|is_stale|true|false|
|expanded/TW_M1B_M2|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|indices/SP500|status|stale|ok|
|indices/SP500|is_stale|true|false|
|indices/SP500|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|indices/DJIA|status|stale|ok|
|indices/DJIA|is_stale|true|false|
|indices/DJIA|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|
|indices/NASDAQCOM|status|stale|ok|
|indices/NASDAQCOM|is_stale|true|false|
|indices/NASDAQCOM|reason|快取超過有效期；僅供顯示，不能作最新驗證|null|

逐步失敗、恢復及部署紀錄：deployment-01-preflight.md 至 deployment-06-four-models.md；所有內容均為實際執行結果，沒有把下一步計畫寫成完成。
