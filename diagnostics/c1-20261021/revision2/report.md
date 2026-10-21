# C1 修訂2：完整性補強已在本機驗收，未部署

日期2026-10-21。正式站仍v231，本輪未發布、未合併、未改正式資料。前一輪C1驗收後續查，按擁有者指示邊完成邊紀錄。

## 修補及實際證據

|問題|修補前反例|修補後|
|---|---|---|
|EPS重複列灌高證據數|同一historical列複製兩次，可誤算兩組|只計historical／model／ttm／consensus不同口徑；日期／正值／來源檢查仍保留|
|同口徑矛盾|同一EPS id不同數值仍可算證據完整|數值、日期、期間或來源矛盾時，估值證據不完整並明列缺口|
|技術分數與明細不符|四條皆−1但總分+4、或重複週期仍可算技術完整|四種週期各一條；價格、均線與斜率方向必須對應貢獻，總分須等於加總|
|正式VETO欄位|clear標籤但assessmentCounts.unknown=4時可顯示高信心|同時核對巢狀未知數及逐條rules，不把未知當安全|

增加reasonDetails內實際使用的EPS與市場證據日期／來源，方便交接追溯。沒有更動C2分歧計算、既有Gate、權重、評級或風險許可。

## 測試

- 新增4項反例：修補前4項皆失敗，已保存[修補前完整輸出](regression-before.log)，沒有把未執行測試寫成完成。
- 修補後advisory／display **24/24**，fail0：[修補後輸出](regression-after.log)。
- 完整 **npm test exit0**：legacy全鏈、calendar9/9、advisory integration51/51、fixpack4/4、C2 5/5，fail0；[完整輸出](npm-test.log)。
- git diff --check通過；build reproducibility兩次重建一致。
- 乾淨v231基線重新套本輪patch並build，HTML／Worker與受測版本位元組相同，SHA見[manifest](manifest.json)。

## 逐檔比較

[相對正式v231的完整C1前後比較](before-after.json)，另有[相對前一輪本機C1比較](previous-c1-comparison.json)。兩組使用完全相同凍結輸入；不是新的正式站讀回。

|代號|相對前一輪本機C1的結論|信心|正式評級與風險許可|
|---|---|---|---|
|8299|不變：估值分歧、技術偏弱，現金流警訊保留|低→低|未評／not_cleared，不變|
|5289|不變：估值分歧、技術偏弱，現金流警訊保留|低→低|未評／not_cleared，不變|
|2404|不變：估值分歧、技術偏弱|低→低|未評／not_cleared，不變|
|5009|不變：現金流保守觀察、技術偏強|低→低|C／not_cleared，不變|

四檔共40個Gate完整物件、scoring、VETO、adaptiveRating、primaryValuation完全相同。新增來源追蹤欄位；5009缺口文字更明確為「不同口徑」EPS。本輪修補封住矛盾／重複輸入，正常輸入不產生任意評級跳動。

凍結重播仍缺台股240日線、利差20日、11類股同口徑完整觀測；未供獨立歷史快照的重播不能代表正式站來源損壞。本輪沒有補造資料，也未解決其他待辦來源或啟用持股比例。

## 唯一應用方式與完整diff

乾淨基線 `6b924076503a47e346a3d72ff3efeb5260a8078f` → [本輪完整c1.patch](c1.patch) → node build.mjs → npm test。**不要先套舊C1再疊本輪patch：這是相對v231的完整取代patch。**

來源diff含C1計算、顯示、測試與受build同步的HTML；生成Worker按build重建，避免公開私人操作說明。公開內容未包含私人網站入口／專案ID／真憑證或Tiingo原始價格。

patch SHA-256：`e0f90ba015cb04becdb92a9e70ef0504785ed7c18488cbaefc56bd21e285bf7f`。
HTML：`eae525566ee411db961d80aeab595db49184c39594de04558964687ac2815677`。
Worker：`ebde53e133d2cc30ec5ccb1d7fe88c605d0dc1cd85a0907d451255e44d82c70e`。

## 接手狀態

本機修訂2完整驗收完成，尚未經外部獨立審查、尚未部署。後續以此版本審查；正式站仍v231。不得將工程完成當作所有資料缺口消失，不自動通過Gate、不改權重或風險預算。

[05問題先記錄](../05-integrity-review.md) → [06修補後紀錄](../06-integrity-fixed.md) → 本報告。前一輪patch／報告保留供歷史追蹤。
