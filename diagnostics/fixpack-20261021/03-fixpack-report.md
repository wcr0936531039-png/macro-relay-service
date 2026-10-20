# 修正包本機驗收完成 — 2026-10-21（未部署；C2尚未套用）

## 範圍與可重放補丁
只含待辦#3、B1、B2七項。正式站維持v230，沒有push網站來源、存版本或部署。C2將在本報告保存後另做。

基線為網站已發布來源 f9c5f15b371de58d0a06ef5251ce5c8a895f217e；中繼main輸入指紋已列在01-scope.md。中繼為資料與交接倉庫，修補目標是原網站，不把網站patch誤套在中繼服務程式。

[修正包patch](fixpack.patch) SHA-256：`d69ac5bb2538c9b3115306eb8c490077797b284a69e9c07151dbcf560bae6d0c`。
保留最初checkpoint及SHA檔供追溯；後續修正以fixpack.patch為準。補丁包含原始碼、HTML、測試；不含生成的dist/server/index.js，其上下文含不應重複貼出的內部操作說明。乾淨基線git apply後執行node build.mjs可重建Worker；無須任何秘密。

## 固定目錄與融資最終值
原API65列其實只有55個不同指標，10個重複id為NYFED_REPO、TWSE_TAIEX、TWSE_TOTAL_TRADE_VALUE、TWSE_MARGIN_BALANCE_NTD、TWSE_MARGIN_CHANGE_NTD、TWSE_MARGIN_BALANCE_UNITS、TWSE_SHORT_BALANCE、TWSE_SHORT_CHANGE、TWSE_BREADTH、TWSE_DAYTRADE。
因此採固定去重核心55、市場36；缺項仍輸出missing，不用重複列湊65。擴展12項保留獨立來源、評分及畫面；不混入核心分母。頂部與Gate使用同一核心口徑。這項根因修正與交接原先假定的65不同，請擁有者審閱；未擅自部署。

官方統計匯入時，保存當日今日餘額為provisional；用下一份官方報表前日餘額，修訂原交易日為final，記下reportedDate、fetchedAt、來源及before/after修訂。由官方交易日序列決定前日，不用日曆減一天；不造週末值，不接受舊暫定資料覆蓋最終值。
10/19融資金額原640,618,432仟元→10/20公布前日640,617,928仟元：保留10/19觀測日，修訂−504仟元；10/20自己的餘額仍暫定。融資／融券日變化按已觀測餘額重算；同日市值有保存才重算歷史融資占市值比，沒有分母時不借用隔日市值。修訂另存私人持久歷史，不覆蓋原始證據鏈。

## B1前後比較（同一凍結輸入，本機重播）
SP500 10/19：−1.492333%→+0.408516%，比較起點改為10/16。
WTI 10/14：+7.251105%→+1.041047%，比較起點10/13。
Henry Hub 10/14：+1.898734%→+2.547771%，比較起點10/13。
數值採來源相鄰觀測，保留起訖日；只有多日變化的舊快照不再冒稱單日。六個TWSE指數10/20的原官方漲跌均可對回10/19收盤，不另改正確的官方單日漲跌。

US總經：59→65。
- 美股波動與指數動能：45→62.5。
TW總經：58→59。
- 台股本土景氣／廣度／交易：41→45。
既有公式、權重、門檻未改。這不是承諾改善投資環境，而是修正原本把5筆變化當單日的輸入。比較基準是本輪凍結資料，不把先前手機截圖的不同時點數字混進前後比較。

四檔本機同資料比較：

|代號|退避評級前→後|原始總分前→後|Gate狀態變化|風險許可|
|---|---|---|---|---|
|8299|D→D|null→null|0|not_cleared→not_cleared|
|5289|D→D|null→null|0|not_cleared→not_cleared|
|2404|D→D|null→null|0|not_cleared→not_cleared|
|5009|C→C|null→null|0|not_cleared→not_cleared|

Gate4/5/8缺項、Gate6財報警訊、未知否決條件均保留；沒有自動通過Gate，也沒有提高風險預算。

## B2七項
1. 早晚巡檢文字改06:30／22:30，與既有任務設定一致；本輪沒再改排程。
2. 美國指數標題顯示本輪實際provider，FRED不再被寫成Yahoo。
3. 頂部類股表本來即呼叫同一/api/us-sector-report；改掉靜態Yahoo池註腳，依主要／備援來源與priceField顯示Tiingo或Yahoo獨立序列。
4. 覆蓋率統一核心目錄；擴展資料仍可見，另揭露自己的覆蓋，不以合併列數改核心分母。
5. 明列後台本輪更新數、此瀏覽器追蹤數及未涵蓋代號；說明後台與私人清單分開，不把4檔更新說成私人5檔全數完成。
6. 金銀比operands與金銀卡片使用同一核對快照數值和時間，避免不同時點報價混用。
7. D→D改為已是最低級、保留時機警訊；均線改為−4（範圍−4～+4），沒有改分數。

## 驗證
完整npm test exit0，包含所有legacy、38項既有advisory integration、build reproducibility及4項新增fixpack測試。git diff --check通過。額外測試確認擴展rows保持可見，核心覆蓋仍按核心catalog計算。
固定目錄測試覆蓋空資料／重複id／缺值；融資測試覆蓋原日修訂、週末不造值、舊匯入不得覆蓋final、修訂軌跡；金銀測試確保卡片與比值operand相同。
原測試有三處跟著舊假設走：小型automation fixture原被判整個市場ok，現在如實partial；CPI和市場時效測試由rows[0]改按指標id查找。原來的來源、日期與有效狀態斷言保留，未刪除檢查以湊通過。

原始前後比較：[before-after.json](before-after.json)；完整測試輸出另存npm-test.log。patch與測試都不包含Tiingo真實原始價格或憑證。
