# 2026-10-25 本機三項修補 checkpoint

基線：488b8bc9ab0402472496a80abb1cee17aea35fae（正式 v233 原始碼）。本輪未部署、未推送網站來源分支。

已讀 Claude 2026-10-25 14:40 節。已完成初版：

1. 信用最新交易日改採官方 FMTQIK 實際最後交易日；預定行事曆僅保留 expectedSession／calendarDiscrepancy 證據，不再因臨時休市拒收。仍驗證官方來源、日期、值、擷取有效期，並保留20日最大觀測界線；10/26補假測試已加入。未將10/22今日餘額升final。
2. deferred 信用不得以快照checkedAt或當下時間補成verifiedAt；本輪檢查另存checkedAt。缺原來源時間則保留缺項，不能修復過去已被錯寫的時間。
3. finalize 每個checkpoint重讀一個與畫面相同的API，存summaryScope=final_readback及readbackAt，history採最後摘要。保留板塊30次上限。擴展總經／股指在回應快取過期時改逐列按觀測與原擷取有效期判定，不再整包強制stale。

初步測試：信用與持久化／接續35/35；新增回歸8/8；原observation-freshness通過。首輪發現finalize會把已達30次的partial改回pending，已修正並重跑通過。

下一步：完整npm test、基線與修改版同輸入前後比較、完整diff與SHA-256。測試結果尚未齊全，不能將本checkpoint當成部署驗收。
