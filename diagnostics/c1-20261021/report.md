# C1 綜合判斷：本機驗收完成，尚未部署

日期：2026-10-21。基線：`6b924076503a47e346a3d72ff3efeb5260a8078f`（正式v231）。依擁有者「綜合判斷先完成、逐項紀錄」指示；沒有部署、合併、修改正式站資料或發起額外收集。

## 本輪完成

|項目|實際結果|
|---|---|
|明確結論|既有VETO優先；EPS分歧保留未評；負現金流保留保守觀察；另列技術方向。|
|證據信心|高／中／低；任一估值／技術／總經證據類不完整＝低，三類齊但估值分歧／否決未知＝中，三類齊且無上述限制＝高。這是透明顯示規則，不是回測勝率、投資分數或風險許可。|
|三方面理由|固定依序估值、技術、總經／市場，不再用任意slice截斷而遺漏某方面。|
|改判條件|依EPS既有分歧界線、實際偏強／偏弱均線、240日線及利差／類股缺項產生；新財報才重算現金流；原否決須原規則逐條核驗。|
|缺口與警訊|缺值、過期、未來觀測及股號不一致不當安全；已核算CFO與FCF警訊獨立列出。|
|顯示|主要理由、警訊、改判條件、信心限制直接顯示；原始計算仍可展開。|

未啟用草案因子加減分／持股比例，未改分數、權重、原Gate、VETO、C2估值分歧、風險預算。四公司指引比較面板仍暫緩。沒有自動通過Gate5A／5B／8。

## 測試與再現

- 原有advisory／display測試11項先通過；新增測試首次19/20，找到有年線但缺利差時改判條件不夠明確，已先記錄再修正。
- 修正後針對性20/20，fail0（新增9項）。
- **完整npm test exit0**：legacy整條成功、calendar9/9、advisory integration47/47、fixpack4/4、C2 5/5，fail0。含兩次build byte-identical檢查。
- git diff --check通過。
- 另開乾淨基線工作樹，套用本次完整來源patch後build；HTML／Worker與受測版本SHA逐一相同。
- 完整[測試輸出](npm-test.log)、[完整來源diff](c1.patch)、[四檔前後每列比較](before-after.json)。編譯Worker以build重建，未公開含私人操作說明的整份編譯上下文；來源patch包含worker、測試與受build同步的HTML，足以重建。

## 四檔相同輸入前後比較

使用已保存10/21輸入與10/20價日、相同總經／市場／scanner及來源證據重播；明確不是新增正式站讀回。此重播未供獨立跨市場歷史，不能把本輪缺口推論成正式站資料損壞。

|代號|C1文字結果|證據信心|原評級／風險許可|
|---|---|---|---|
|8299|估值分歧10.69倍；技術偏弱；CFO／FCF警訊保留|低（2/3）|未評／not_cleared，不變|
|5289|估值分歧14.63倍；技術偏弱；現金流警訊保留|低（2/3）|未評／not_cleared，不變|
|2404|估值分歧3.12倍；技術偏弱|低（2/3）|未評／not_cleared，不變|
|5009|保守觀察現金流；技術偏強|低（1/3）|C／not_cleared，不變|

四檔共40個Gate完整物件逐一不變；scoring、VETO、adaptiveRating（含riskPermission）、primaryValuation逐一相等。C1 activeScoreContribution=0、appliedToRating=false、appliedToRiskBudget=false，holdingSuggestedRange=null。

低信心原因：凍結重播的年線／利差20日／11類股同口徑證據不齊，既有否決尚未知；前三檔另有估值分歧；5009可追溯有效EPS組數不足。沒有補造來源，沒有把工程完成寫成資料全齊。

## SHA-256

|檔案|SHA-256|
|---|---|
|c1.patch|cf88795b379efab63f6844c12054e2208721447158108d20a0616d55af40bf44|
|npm-test.log|07973a89d1820736d613e8140a6c610f5c949edc1f72fcf2bf0b4ed28d58327d|
|HTML|eae525566ee411db961d80aeab595db49184c39594de04558964687ac2815677|
|Worker|6e4cdbae3e09e2e208b3b1638402d81a088e8acbfc27ee5d8b13caf730fdb03d|

公開patch、比較及log已檢查不含私人網站入口／專案ID／真憑證；比較只保留C1必要欄位，不公開Tiingo原始價格。

## 後續與審查

本機程式與測試驗收完成，仍須獨立審查與擁有者部署授權。正式站維持v231，不得將此報告當作正式站新功能已上線。
[Gemini固定讀取指引](../GEMINI_HANDOFF.md)；審查者請依此處完整diff和測試核驗，區分顯示完成與上游資料缺口。

## 過程紀錄
[01範圍](01-scope.md)、[02計算顯示](02-calculation-and-display.md)、[03測試發現缺口](03-test-found-gap.md)、[04修正與重播](04-targeted-and-replay.md)。
