# v232 部署與正式驗收結果

2026-10-23 08:49:56（台北）部署成功，08:58:47 完成本輪正式巡檢。擁有者優先指定的整合部署、正式保存驗收及恢復既有排程已完成；實際晚間新信用資料捕獲、翌晨跨日保持仍待後續排程驗證。整站資料狀態保持 **partial**。

## 交付與版本

- 正式版本 v232；來源 commit `3cf3a936ba80b94aa184054a2a75b53244668476`，基線 v231 `6b924076503a47e346a3d72ff3efeb5260a8078f`。v231 保留回滾，擁有者私人受眾不變。
- C1 綜合判斷顯示完整理由、證據信心、具體改判條件與缺項。信用22:30閘門同時覆蓋大盤與個股路徑，分開驗證觀測日、擷取時間與必要餘額欄位。
- 整站巡檢使用持久 checkpoint；POST 保存開始，持續 GET 每次推進一步，冷 Worker 可接續同一 runId。新增保存失敗上拋與讀回、逐項失敗隔離、啟動／執行租約、前端輪詢相容性。
- 這個執行模式需要持續輪詢；不能寫成 POST 後無人輪詢也保證完成。未改五大維度權重、Gate規則、總分公式、風險預算或草案計分開關。

|檔案|SHA-256|
|---|---|
|正式首頁 HTML|`080f721d52eb610eb245a5a7f6a1fa630bc42e12740828d3fc3e5207c4186d3d`|
|部署 Worker|`cee5f3724e4ea9a32abb0a84985d80c7b63561e47fd846c21bd4c2733978f4fa`|
|部署封裝|`dc06d8c44e331a056d56f3e9502bec520dc9f4e35d8194bda37ad557b96135b3`|
|[完整已部署來源 diff](deployed-source.patch)|`ae5a3addc52d64245a1c0430c6e17ff49ca9d14df504615cad1663d866214f3a`|
|[測試 fixture 補丁](reliability-deploy-fixture-only.patch)|`21366a9f32662d6c2e22066d1ec495eec82283c6e5430bc3d0addf7d7c5cfe6d`|
|[部署前完整 npm test](deployment-final-npm-test.log)|`ee6da8d8aab4abe4b484e7cf1f8bd60f27863612fb5968e23bf877016f5727f5`|

正式首頁讀回雜湊與受測版本相同；部署包只使用已推送來源的當前建置檔與未變動遷移，不混入舊 Worker。

## 測試與實際遇到的失敗

部署前重新跑完整 `npm test`，最後 exit 0；legacy、calendar 9、advisory 51、fixpack 4、C2 5、reliability 32 項均通過。相同新輸入的 v231／v232 控制比較，四檔40個 Gate 完整物件、scoring、VETO、adaptiveRating、primaryValuation 均相同，風險許可均 `not_cleared`。[控制比較逐格結果](deployment-identical-live-inputs.json)。這不是不同時刻正式資料的前後比較；控制輸入對時效旗標做一致處理，不能用來宣稱來源或實際盤勢沒有變化。

首次完整測試失敗也保留：8299 自動巡檢測試漏 mock 外部請求，導致 `step_timeout` 與未滿4個audit。定位後只把測試 fixture 未定義上游改成立即503，保留原4/4保存斷言；未改正式 timeout 或放寬斷言。[首次失敗](deployment-02-preflight-failure.md)、[定位](deployment-03-timeout-diagnosis.md)、[重跑通過](deployment-04-preflight-pass.md)。

來源推送成功後，既有 helper 因缺 `package-site.sh` 而封裝失敗；按前版已成功封裝的10檔布局，用當前來源手動重建、驗雜湊，原生部署最後 succeeded。[封裝失敗紀錄](deployment-05-package-block.md)、[部署成功](deployment-06-published.md)。

## 正式 run、歷史與四檔保存

- runId：`11fa1981-e6b8-49d7-bdb1-5f872c7e458a`。
- startedAt：`2026-10-23T00:51:16.474Z`；completedAt：`2026-10-23T00:58:47.699Z`；status：`partial`；checkpoint：`done`。
- 歷史讀回 runId、completedAt 完全匹配；stockCount 4、researchCount 4、gateAuditCount 4。四檔audit均 `recorded:true`，每檔10個 Gate。
- 正式 status 請求均成功推進 checkpoint，讀回沒有整輪 waitUntil 被取消。此結論限本輪服務巡檢，不把其他畫面請求的401、404或取消也說成不存在。

|股票|已保存 audit|正式評級|風險許可|
|---|---|---|---|
|8299 群聯|10 Gate，recorded|未評（估值分歧）|not_cleared|
|5289 宜鼎|10 Gate，recorded|未評（估值分歧）|not_cleared|
|2404 漢唐|10 Gate，recorded|未評（估值分歧）|not_cleared|
|5009 榮剛|10 Gate，recorded|C／保守觀察|not_cleared|

四檔 C1 證據信心均低，缺項與警訊未自動升級。本輪5289行情步驟曾回 `pending` 與10/22舊擷取時間；後續獨立讀回為10/23新快照，兩者分開保存，不倒改 run 原結果。服務身分更新的是預設四檔批次，不宣稱已讀取個人私人追蹤清單。

## 資料覆蓋與來源缺口

|模組|run 保存狀態|實際結果與限制|
|---|---|---|
|核心總經|ok|55/55不同指標；沿用已核准固定目錄|
|擴展總經|partial|11/12；`TW_EXPORT_ORDERS` 403，2026-09觀測保留stale|
|市場／貴金屬|ok|36/36可用；不代表20日歷史已齊|
|美股指數|ok|3/3|
|跨市場|ok|4/4；原擷取時間10/22不改成今天|
|美股板塊|error|本輪模組逾時；其餘模組與四檔保存仍完成|
|官方公告|ok|3/3；BLS主RSS未得近期文章，官方備援成功，主失敗另存|

後續獨立板塊讀回 **11/11**，Tiingo `adjClose` 主要來源，sourceCoverage 12/12；與Yahoo比對 `within_guard`，最大差 `0.000012146001671098361` 個百分點。觀測日仍 **10/21**，generatedAt `2026-10-23T00:53:40.984Z`；既有NYSE收盤+15分鐘後8小時發布寬限不變，不標成10/22，也不把原run逾時改寫為成功。這次可靠性部署未調板塊來源策略或來源保護門檻，板塊間歇逾時仍需後續觀察。

- 全市場：10/22 **1,947/1,985檔（98.09%）**、72個交易日；TWSE 1081/1091、TPEx 866/894，仍缺38檔。warmup 5、needsReview 13；全站72日不代表每檔60日完整。
- 八條FRED序列已重新取得並正式匯入；核心CPI **2026-09=338.896**，BLS與FRED同月同值、verified並讀回。原擷取與核對時間分開保存。
- 八組來源匯入 **236筆、錯誤0**：twse119、tpex30、semiconductors10、display10、energy10、consumer0、steel7、aviation50；consumer仍0不能說研究已補齊。
- 逐檔來源池：8299 partial 5筆、TrendForce Semiconductors403且stale；5289 4筆、2404 1筆、5009 2筆，後三檔讀回無來源錯誤。整批匯入成功不抵銷個股來源失敗。
- 金銀比歷史 **17/21**，仍不足20日趨勢；沒有補造缺值或啟用新評分。
- Gate4／5／8及CB、VETO未知保留；群聯Gate6 **CFO／淨利−0.17倍、FCF−141.57億元**是真實財報警訊，沒有改成資料不足或綠燈。

## 早晚信用限制與排程

本輪為上午，正式大盤7項信用欄位皆 `captureDeferred:true`，值、10/21觀測日與原擷取時間 `2026-10-22T02:19:38.764Z` 完全保留。這個舊擷取時間是10/22上午，不稱為昨晚新資料，也不宣稱信用已對齊10/22。

四檔個股最終獨立讀回皆 `marginCredit.status:deferred`、records 0、capturedAt null、marginDate null。尚無新的獨立晚間個股快照時保留待抓，records 0不是餘額為零。初讀2404／5009舊 pending 結果未當作驗收，等新快照完成後再核對四檔。[四檔信用讀回](deployment-11-credit-all-four.md)。

既有每日巡檢已恢復，Automations與Sites關聯狀態均讀回啟用；時區Asia/Taipei、06:30／22:30，沒有新增重複任務。工具 `next_run_time` 仍null，不能宣稱下一次已觸發。操作提示已保存並完全讀回，規定上午market-only＋不含信用的macro wrapper，晚間等實際22:30才收信用；持續輪詢同run、驗證歷史及audit、失敗有限重試與逐項記錄。[排程恢復讀回](deployment-13-automation-resumed.md)。

**待實際驗證：**首次22:30後的新大盤／個股信用捕獲，及翌晨保留原日期／擷取時間；融資final隔日修訂的連續性。這些未發生的結果不由本機測試代替，交由既有巡檢接續記錄。

## 交接入口與保存規則

[去除私密資料的正式讀回證據](deployment-readback.json)、[部署manifest](deployment-manifest.json)、[相同輸入比較](deployment-identical-live-inputs.json)、[完整來源diff](deployed-source.patch)、[完整測試](deployment-final-npm-test.log)。每個部署步驟deployment-01～13保留，最上層 `diagnostics/latest.md` 是接手入口，較舊的「未部署／驗收中」文字保留為當時紀錄。

10/22第二run本輪補讀回確認partial完成、history與4/4audit；不竄改當時「尚未驗收」的紀錄，也不抹去第一run因waitUntil取消的故障。

公開報告只含狀態、計數、必要公開指標與來源核對摘要；不含服務憑證、私人網站入口／專案識別、內部操作說明全文或Tiingo原始價格。來源缺口、低信心及真實財報警訊繼續保留，不宣稱整站全數完成。
