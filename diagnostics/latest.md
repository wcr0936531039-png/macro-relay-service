# 最新：2026-10-21 修正包＋C2 已部署 v231（正式讀回核對中）

擁有者已直接授權本次部署。已按07:45條件從乾淨 f9c5f15 依序套用兩份已核准 patch、各 build，四項 SHA 均吻合；部署前完整 npm test exit 0。來源 commit `6b924076503a47e346a3d72ff3efeb5260a8078f`。原生部署 succeeded，v230 保留為回滾點，未改存取權限。

官方10/20信用資料已成功匯入並讀回：前一交易日final=10/19，修訂歷史9筆。全站更新已完成 partial，匹配runId的歷史已保存。正在讀回各API與Gate；不把此階段當作全部驗收通過。

**部署前已存在的缺口**：四檔實際Master已因行情／估值／財報快照過期或FinMind HTTP402而blocked，風險許可均not_cleared。凍結資料C2重播則仍符合三檔未評、5009 C。正式與凍結結果將分開列出。Tiingo最新交易日缺漏已退至Yahoo備援，亦先於本部署發生。

逐步紀錄：[部署前檢查](fixpack-20261021/deployment-01-preflight.md)、[真實基線缺口](fixpack-20261021/deployment-02-live-baseline.md)、[完整測試通過](fixpack-20261021/deployment-03-tests-passed.md)、[部署成功](fixpack-20261021/deployment-04-published.md)、[本輪全套測試輸出](fixpack-20261021/deployment-npm-test.log)。本頁將在讀回結束後更新最終結果。

---

# 修正包與C2本機驗收完成 — 未部署

兩組都已依序完成全套 `npm test`，退出碼皆為0；完整diff、SHA-256、前後比較與測試輸出均已保存。

- 修正包：[完成報告](fixpack-20261021/03-fixpack-report.md)、[patch](fixpack-20261021/fixpack.patch)、[SHA](fixpack-20261021/fixpack.sha256)、[全套測試](fixpack-20261021/npm-test.log)。US59→65、TW58→59源於B1單日變化修正；四檔原退避評級D/D/D/C與Gate狀態不變。原65列含10個重複id，固定核心目錄實為55；市場固定36，缺值保留；擴展12項仍可見且分開計算覆蓋。此口徑根因已列報，沒有湊65。
- C2：[完成報告](c2-20261021/03-c2-report.md)、[patch](c2-20261021/c2.patch)、[SHA](c2-20261021/c2.sha256)、[全套測試](c2-20261021/npm-test.log)。8299／5289／2404改為未評（估值分歧），5009維持C；四檔Gate、scoring、VETO、財報警訊與風險許可均不變。

補丁順序：網站來源 f9c5f15 → 修正包 → build → C2 → build。修正包本機commit4aadab203b6dc7c92b91ac35572ec14b1e74eaf7；C2本機commit594b8b30d5abcb48fb1b39bfa942c02b155d580d。兩個來源補丁都在乾淨基線串接重放，最終HTML SHA-256 `93d22d219109e52161e0e85ab926ad86dab6fadfc5083c57144e5c21b1f9e638`；Worker SHA-256 `613ac53005c0346259bf4aff78f95e18ced8c4c29a81f1d964ff9b4a56e79675`，與本機一致。

沒有網站來源push、儲存部署版本或部署；正式程式仍維持v230。原始Tiingo價格與憑證未上傳。其他回測計分／持股換算／C1、C3、C4未做。請擁有者看完報告再另行授權部署。

---

# C2估值分歧本機驗收 — 2026-10-21（未部署）

修正包報告03-fixpack-report.md已先完成並上傳，才在其本機commit 4aadab203b6dc7c92b91ac35572ec14b1e74eaf7之上實作C2。這份只列C2改動，不把修正包的總經變動算進C2。

[僅C2補丁](c2-20261021/c2.patch) SHA-256：`9ad8c47bae31fa31008f88895b8a40e3f46fbf9ec6d94f505c6215dd69ad34e4`。
套用順序：原網站來源f9c5f15 → fixpack.patch → node build.mjs → c2.patch → node build.mjs。兩個source patch均已在乾淨基線依序重放，生成HTML與Worker與本機逐位元相同。不包含生成Worker內的內部操作上下文；沒有Tiingo真實原始行情或憑證。

## 規則與狀態
四個口徑：跨週期完整年度EPS中位數、今年模型EPS、TTM EPS、Gate8已判有效的當年度共識。缺值、非正值、非當年模型或未通過Gate8的共識都不參與，保留原因。
至少兩值且max/min嚴格大於2才觸發；恰好2不觸發。觸發後grade=null、valuationGrade=null、label=未評（估值分歧）、outputStatus=not_rated；不是拿D冒充未評。原始模型分數不變。
現金流與財報警訊、均線下方、未知否決與原預算限制保留；實際VETO優先。沒有啟用任何新增總經加減分或持股換算。

## 同資料比較
|代號|原退避評級|C2結果|max/min|Gate狀態變更|原風險許可|
|---|---|---|---|---|---|
|8299|D|未評（估值分歧）|10.6915|0|not_cleared（不變）|
|5289|D|未評（估值分歧）|14.6323|0|not_cleared（不變）|
|2404|D|未評（估值分歧）|3.1180|0|not_cleared（不變）|
|5009|C|保守觀察|1.5171|0|not_cleared（不變）|

四檔scoring、veto與財報風險敘述深度比對不變；總經計算C2前後完全相同，維持修正包的US65／TW59，C2沒有再動總經分數。

### 8299

- 歷史常態EPS（跨週期中位數）：39.0000；2025-12-31（資料所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 今年模型EPS：206.8830；2026-10-20（模型評估基準日）；分析師人數 不適用；來源 FinMind TaiwanStockFinancialStatements + TaiwanStockMonthRevenue https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 近四季EPS：220.2000；2026-06-30（財報所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 當年度有效分析師共識：416.9700；2026-10-13（共識原更新日）；分析師人數 11；來源 FactSet／鉅亨公開報導 https://gfemobile.cnyes.com/news/id/6629082。

下次財報：2026 Q3 2026-11-14（法定期限）。

### 5289

- 歷史常態EPS（跨週期中位數）：12.2321；2025-12-31（資料所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 今年模型EPS：174.8012；2026-10-20（模型評估基準日）；分析師人數 不適用；來源 FinMind TaiwanStockFinancialStatements + TaiwanStockMonthRevenue https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 近四季EPS：178.9841；2026-06-30（財報所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 當年度有效分析師共識：不參與：缺90日內、同股票同年度TWD共識來源；日期缺值（共識原更新日）；分析師人數 不適用；來源 缺值 。

下次財報：2026 Q3 2026-11-14（法定期限）。

### 2404

- 歷史常態EPS（跨週期中位數）：21.2800；2025-12-31（資料所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 今年模型EPS：54.2090；2026-10-20（模型評估基準日）；分析師人數 不適用；來源 FinMind TaiwanStockFinancialStatements + TaiwanStockMonthRevenue https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 近四季EPS：66.3500；2026-06-30（財報所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 當年度有效分析師共識：不參與：缺90日內、同股票同年度TWD共識來源；日期缺值（共識原更新日）；分析師人數 不適用；來源 缺值 。

下次財報：2026 Q3 2026-11-14（法定期限）。

### 5009

- 歷史常態EPS（跨週期中位數）：2.2000；2025-12-31（資料所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 今年模型EPS：3.3377；2026-10-20（模型評估基準日）；分析師人數 不適用；來源 FinMind TaiwanStockFinancialStatements + TaiwanStockMonthRevenue https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 近四季EPS：2.2000；2026-06-30（財報所屬期末，非發布日）；分析師人數 不適用；來源 FinMind EPS＋股利／分割／面額變更資料 https://finmind.github.io/tutor/TaiwanMarket/Fundamental/。
- 當年度有效分析師共識：不參與：缺90日內、同股票同年度TWD共識來源；日期缺值（共識原更新日）；分析師人數 不適用；來源 缺值 。

下次財報：2026 Q3 2026-11-14（法定期限）。

來源日期明確區分資料期末、模型基準日與共識更新日，沒有把期末假裝成發布日。
本輪沒有取得新的公司公告財報日，故顯示本次授權的曆年制法定期限；不是捏造已公告日期。新增經原官方來源驗證的earnings_schedule匯入契約，取得公告後可優先顯示公司日期。新季度財報進入既有資料管線，EPS分歧和下一期別自動重算。

## 測試與限制
完整npm test exit0：所有legacy、38項advisory integration、build reproducibility、4項fixpack與5項C2測試全數通過。C2測試含群聯四值、負／缺值排除、恰好2倍、無效共識排除、風險限制不放寬、實際VETO優先、已驗證公司日期優先、季度更新後重算，以及主畫面確實顯示未評面板。
四份真實財報輸入的本機C2報告均通過DOM renderer；不是宣稱正式站已更新或完成瀏覽器／手機新畫面驗收。正式站仍v230；未push網站來源、未保存部署版本、未部署。

完整數值：[before-after.json](c2-20261021/before-after.json)。完整測試輸出：npm-test.log。請擁有者審閱後另外授權部署。
