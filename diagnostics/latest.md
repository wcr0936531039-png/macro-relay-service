# 最新：2026-10-29 06:50 台北晨間巡檢完成，partial

[本輪記錄](automation-runs/20261029-morning.md)。

run c8d3426d-32db-4095-bc3f-cfba658798e9：POST HTTP 202，連續 status HTTP 200 至 completedAt 06:50:29（台北），history HTTP 200 匹配成功；Gate 快照 5/5。watchlistSource=latest_synced，stockBatch=5。總經 55/55、擴展 12/12、市場／貴金屬 36/36、美股指數 3/3、跨市場 4/4、板塊 11/11、公告 3/3；全市場 1,959/1,988（98.54%）。

晨間信用收集按時段略過；讀回仍為 10/28 snapshot，但缺 capturedAt／verifiedAt／captureDeferred，隔夜時間連續性標未驗證。核心 CPI 雙來源通過；八組研究來源 312 筆。partial 與其他缺項、前次行情 IncompleteRead 重試成功詳見本輪記錄。未修改程式、排程、權重或 Gate 門檻。

---

# 最新：2026-10-29 04:43（台北）巡檢完成，狀態 partial

[本輪紀錄](deploy-20261026/hotfix6.md)。

同一 run 完成並由 history 核對（POST 202、status 33/33 HTTP 200、history 200；Gate snapshots 5/5 recorded）。核心總經 55/55、核心 CPI 雙來源同月同值、全市場 1,959/1,988（98.54%）、來源 8/8 組 289 筆。未解項與讀回差異見報告；未更動權重、風險預算或排程。本輪為上午巡檢，信用統計按時段略過，既有 10/28 快照及 verifiedAt 保留。

---

# 最新：2026-10-28 22:30 晚間巡檢完成（partial）

[本輪完整紀錄](source-reliability-20261023/2026-10-28-night-run.md)。

網站 run `1266920c-a004-4f7f-aa62-4281531514c4` 已按 POST → 10 秒 status → history 流程完成；history 匹配 completedAt，Gate 5/5、latest_synced 5 檔均保存。全市場 1,959/1,988、74 日；總經 55/55、板塊 11/11、來源 8/8。partial 主因與新發現：國發會燈號過期、三個模組仍標 pending、外部信用收集器 HTTP 307、4 檔 run 摘要與直接讀回不一致、公告原始代號缺口。網站內部晚間信用讀回則為大盤 7/7 與個股 5/5 皆 10/28、ok；未放寬 Gate 或權重。

---

# 最新：第一、二項來源／穩定性修補進行中（正式仍v232）

[開始與範圍](source-reliability-20261023/01-start.md)｜[已重測根因](source-reliability-20261023/02-findings.md)｜[本機與真來源進展](source-reliability-20261023/03-local-progress.md)｜[目前完整patch](source-reliability-20261023/source-recovery.patch)｜[SHA／狀態](source-reliability-20261023/manifest.json)｜[八來源實測](source-reliability-20261023/source-collection-status.json)。

依擁有者「1.2先完成」繼續：Tiingo序列22檔與6秒模組預算不相容，改逐檔保存／同checkpoint分批接續；consumer官方RSS實際空白，官方分類HTML備援已真抓5筆，八來源275筆。外部有效快照與強制重建來源池交接已補測。19項針對性通過，完整npm test正在跑；patch已先保存，尚未部署／未匯入275筆。

MOEA原月表、圖表、新聞、首頁、官方CSV及兩份官方PDF在此環境均403，尚未解決，不用搜尋摘要代替原始擷取或解除stale。原排程啟用；真實今晚22:30新信用捕獲與翌晨保持、手機畫面驗收仍未完成，不預支結果。其餘Gate／面板／回測不混入。

以下v232部署及更早紀錄保留為歷史；本輪未完成項以本節及source-reliability-20261023為準。

---

# 最新：v232已部署，本輪正式保存驗收完成，原巡檢排程已恢復

[完整部署報告](reliability-20261023/deployment-report.md)｜[正式讀回證據](reliability-20261023/deployment-readback.json)｜[四檔相同輸入比較](reliability-20261023/deployment-identical-live-inputs.json)｜[部署manifest／SHA](reliability-20261023/deployment-manifest.json)｜[完整已部署diff](reliability-20261023/deployed-source.patch)｜[完整npm test](reliability-20261023/deployment-final-npm-test.log)。

擁有者優先指定的第一項已部署v232，2026-10-23 08:49:56台北原生部署succeeded；v231保留回滾，私人受眾不變。C1綜合判斷、信用觀測／擷取／內容驗證、保存錯誤讀回、可恢復checkpoint與失敗隔離均已上線。部署前完整npm test exit0（含reliability32、advisory51）；首次測試漏mock外網及helper封裝失敗的定位／處理紀錄皆保留。

第二項本輪正式保存驗收完成：run `11fa1981-e6b8-49d7-bdb1-5f872c7e458a` 於08:58:47台北完成 **partial**，匹配runId／completedAt的history及四檔audit **4/4**讀回，每檔10 Gate。原有06:30／22:30巡檢已恢復，Automations與Sites均確認enabled；沒有另建重複任務。工具next_run_time仍null，下一次實際觸發未預先宣稱完成。此架構需持續GET輪詢才能推進；提示已保存其操作與早晚信用限制。[排程讀回](reliability-20261023/deployment-13-automation-resumed.md)。

上午大盤7項信用保留10/21觀測及原10/22上午擷取時間；四檔個股信用皆deferred、capturedAt:null，未把0筆當0餘額。**今晚22:30後新信用捕獲、翌晨跨日保留及final修訂連續性仍待實際驗證**，不是這次單輪驗收已完成的項目。

核心總經55/55、擴展11/12、市場36/36、股指3/3、跨市場4/4、公告3/3；八條FRED及核心CPI雙來源恢復，2026-09=338.896。全市場10/22為1947／1985、72交易日，仍缺38檔；八來源236筆但consumer0。外銷訂單403、8299 TrendForce403仍保留；板塊在run內逾時，後續獨立讀回Tiingo 11/11、觀測10/21，沒有倒改原run成功。金銀比歷史17/21，20日趨勢仍缺樣本。

四檔40 Gate、scoring／VETO／adaptiveRating／primaryValuation在同一批控制輸入下不變；正式8299／5289／2404仍未評（估值分歧），5009 C／保守觀察，全部not_cleared、C1低信心。Gate4／5／8、CB與VETO未知、群聯Gate6財報警訊繼續保留；權重、總分公式、風險預算未放寬。

下方是歷史檢查點，其「未部署／排程暫停／驗收中」僅描述當時狀態；目前以本節與deployment-report.md為準。下一輪先驗真實跨日信用、記錄板塊間歇逾時與來源缺口，不重複部署已完成成果。

---

# 最新：整合版已部署v232，正式巡檢驗收中，排程尚未恢復

[部署成功紀錄](reliability-20261023/deployment-06-published.md)｜[官方匯入讀回](reliability-20261023/deployment-07-official-import.md)｜[部署前完整測試](reliability-20261023/deployment-final-npm-test.log)。

擁有者已授權優先完成部署與正式驗收。2026-10-23 08:49:56台北原生部署succeeded、版本232；v231保留回滾、私人受眾不變。正式HTML／Worker與核准整合版相同；部署前重跑測試的外網依賴失敗已定位並以純測試fixture補丁處理，完整npm test再跑exit0。

八條FRED及核心CPI雙來源已恢復且正式匯入讀回；市場10/22保存1947／1985、72交易日；八來源236筆、consumer仍0。上午未抓外部信用。

新run 11fa1981-e6b8-49d7-bdb1-5f872c7e458a 已啟動、逐checkpoint進行；尚未宣稱完成與4檔快照全保存。10/22第二run則本輪已補讀回其partial完成、history及4/4audit，保留當時未驗收的歷史紀錄。排程仍暫停，待本輪正式保存驗收可靠後才恢復。

---

# 最新：可靠性修補＋C1本機整合完成，兩套完整測試通過，未部署

[最終報告](reliability-20261023/final/report.md)｜[C1整合完整patch](reliability-20261023/final/combined.patch)｜[可靠性單獨patch](reliability-20261023/final/reliability-only.patch)｜[SHA／套用方式](reliability-20261023/final/manifest.json)｜[整合完整npm test](reliability-20261023/final/combined-npm-test.log)｜[單獨完整npm test](reliability-20261023/final/reliability-npm-test.log)｜[四檔前後比較](reliability-20261023/final/combined-before-after.json)｜[已知問題原表](issue-inventory-20261023/report.md)。

N01／N02信用驗證與N03保存失敗已本機修補；整站改持久checkpoint，GET輪詢每次執行一步，冷Worker接續同一runId，單股研究失敗隔離。新發現的前端輪詢時間／次數不足、同時POST啟動競態也已記錄並修補。32項可靠性測試全過；兩套最終npm test皆exit0，C1整合版advisory51，單獨版38。兩份完整patch各從乾淨v231重建，HTML／Worker雜湊吻合。四檔40 Gate完整物件、評分、VETO、評級與風險許可在相同輸入下不變。

**正式站最後核實仍v231，未部署、未恢復排程。** 不宣稱正式waitUntil問題已解除；需授權部署後用真來源、D1、匹配runId／completedAt／history及跨日信用快照驗收。此架構必須持續輪詢才推進，不能寫成POST後無人輪詢也會自行完成。Gate4／5／8資料缺口、Gate6警訊、FRED與全市場缺項均未以本輪程式修補掩蓋。

最終兩份patch二選一，不疊套信用r2、舊C1或中途patch。各步01～08、修補前失敗及中途全過結果保留在reliability-20261023，接手先讀final/report.md與manifest.json。

2026-10-23補驗：最終8份來源patch／測試／比較檔均已從GitHub重新讀回，與本機逐字相同；manifest與交接索引已核對。[讀回紀錄](reliability-20261023/final/readback.json)。沒有部署或恢復排程。

---

# 最新：已知問題全表已補齊，新增3項本機重現漏洞

[完整問題清單](issue-inventory-20261023/report.md)｜[可重現檢查](issue-inventory-20261023/reproduce.mjs)｜[實際合成輸出](issue-inventory-20261023/reproduction.json)。本輪核對診斷／交接及本機程式，未重跑正式站即時巡檢。

新發現：信用r2只檢查擷取時間、可把2020舊觀測列snapshot；缺餘額欄位仍可列snapshot；巡檢保存失敗false未上拋、函式仍resolved。三項已本機合成重現。**上一輪11項及完整npm test通過仍屬實，但未涵蓋上述反例，信用patch目前不具直接部署準備度，先補修與測試。**報告與manifest已加更正，不竄改歷史結果。

完整清單另列waitUntil取消、無resume、研究失敗隔離、FRED／CPI、全市場28檔缺口、Gate4／5／8、CB／VETO、C1待部署、金價／美元及回測待辦、舊交接過時與歷史已修項。正式站最後核實v231；未部署，排程維持暫停，不放寬權重、評級或風險許可。

---

# 最新：信用時間閘門 revision2 本機完成，待部署授權

[完整報告](credit-window-20261022/revision2/report.md)｜[完整來源patch](credit-window-20261022/revision2/credit-window.patch)｜[SHA與重建資訊](credit-window-20261022/revision2/manifest.json)｜[完整npm test](credit-window-20261022/revision2/npm-test.log)｜[逐列前後比較](credit-window-20261022/revision2/before-after.json)｜[重播工具](credit-window-20261022/revision2/compare-local.mjs)。

大盤官方信用備援及個股FinMind均改為22:30後抓取；上午讀保存快照，保留原日期／擷取時間，缺值與過期照實呈現。新增11項測試、完整npm test全部通過；乾淨v231套patch重建Worker SHA相符。四檔相同凍結輸入的40 Gate、評分、VETO、風險許可均不變。revision2為完整patch，取代revision1，不要疊套。

**未部署，正式站仍v231，排程保持暫停。C1修訂2獨立待審，不混入本patch。** 整站背景任務waitUntil時限取消仍未修復；第二次run輪詢遭自動核准拒絕，無匹配completedAt／持久歷史驗收，不宣稱整站完成。部署本機修補後仍需另行驗證背景執行與跨日保存。初次上線前若無獨立晚間個股信用快照，上午會deferred，不借法人日期補值。

---

# 最新：2026-10-22 信用時間閘門本機修補，第一版全測試通過、續補個股路徑

[逐步巡檢紀錄](automation-runs/20261022-recovery.md)｜[本機檢查點](credit-window-20261022/checkpoint.md)｜[完整來源patch](credit-window-20261022/credit-window.patch)｜[SHA](credit-window-20261022/manifest.json)｜[完整npm test](credit-window-20261022/npm-test.log)｜[前後比較](credit-window-20261022/before-after.json)。

10/21全市場1956／1984（98.59%）、71交易日及8組來源193筆已成功匯入。FRED維護造成8條CSV與CPI核對缺失，照實留缺。第一個整站run因waitUntil時限取消而停在updating_research；後續輪詢被自動核准擋下，因正式站上午仍抓信用，未繞過該限制。無匹配completedAt與歷史完成驗收，不宣稱巡檢全數完成。

官方大盤信用端點第一版本機修補7/7、完整npm test exit0，四檔40 Gate及評分／VETO／風險許可不變；續查個股FinMind融資融券路徑尚未受限，正在補revision2。**正式站仍v231，未部署；排程保持暫停。C1修訂2仍獨立待審，未混入本補丁。**

---

# 最新：2026-10-22 10:12 台北，巡檢恢復讀取、資料收集中

本輪已沿原私人服務存取方式讀回操作說明、全市場狀態與歷史，HTTP 200；前次核准層阻擋本次未再出現。確認正式站 v231、擁有者私人存取、原排程仍暫停。已有70個交易日，因此行情收集只用 sessions=1。上午不抓融資融券／信用統計，保留昨晚觀測及原擷取時間。

官方總經與兩市場行情正在收集；尚未宣稱匯入或整站巡檢完成。C1修訂2保持本機待審，沒有部署新程式。後續逐步補記讀回、runId與實際失敗項目。

---

# 最新：2026-10-22 06:26巡檢被授權層阻擋，排程已暫停

[本輪完整阻擋紀錄](automation-runs/20261022-0626-blocked.md)。

正式站仍為v231且確認擁有者私人存取，但平台自動核准層把完整巡檢誤判成先前本機C1範圍，拒絕使用短期服務憑證讀取私人站API。本輪未取得official-data-tools／market-scanner，未收集或匯入資料，未啟動refresh-all，沒有runId或新增巡檢歷史；不可把舊覆蓋率宣稱成這一輪結果。

為避免反覆產生假巡檢，既有「台股整站每日巡檢」已暫停。這不是官方來源403／503或Worker崩潰。需修正核准範圍後補跑完整巡檢，再恢復排程。沒有洩露或保存服務憑證。

---

# 最新：2026-10-21 C1修訂2本機驗收完成，未部署

[本輪完整報告](c1-20261021/revision2/report.md)｜[完整來源diff](c1-20261021/revision2/c1.patch)｜[SHA-256](c1-20261021/revision2/manifest.json)｜[完整npm test](c1-20261021/revision2/npm-test.log)｜[相對v231前後比較](c1-20261021/revision2/before-after.json)｜[相對前一輪C1比較](c1-20261021/revision2/previous-c1-comparison.json)｜[Gemini固定交接](GEMINI_HANDOFF.md)

續查修補：EPS不同口徑去重／矛盾拒收、均線明細與總分核對、VETO巢狀未知數與rules核對，並保存證據日期與來源。

新增4項反例在修補前均失敗，修補後針對性24/24；完整npm test exit0（legacy、calendar9、advisory51、fixpack4、C2五項全部通過）。乾淨基線套本輪完整patch後build雜湊一致。

四檔40個Gate完整物件、評級、分數、VETO、風險許可均不變；與前一輪C1相比，四檔結論不變，信心仍低。來源缺口照實保留。

**未部署、未合併，正式站仍v231；等待獨立審查及擁有者部署授權。** 本輪patch已含前一輪C1，應從乾淨v231套用，不要重複疊加。

[05發現問題](c1-20261021/05-integrity-review.md)、[06修補紀錄](c1-20261021/06-integrity-fixed.md)。四公司指引面板仍暫緩，未啟用草案評分或持股比例。

---

# 最新：2026-10-21 C1 綜合判斷本機完成，未部署

[完整驗收報告](c1-20261021/report.md)｜[完整來源diff](c1-20261021/c1.patch)｜[完整npm test](c1-20261021/npm-test.log)｜[逐檔前後比較](c1-20261021/before-after.json)｜[Gemini固定交接指引](GEMINI_HANDOFF.md)

- 高／中／低證據信心、估值／技術／總經三類理由、具體改判條件、缺口與現金流警訊顯示完成。
- 針對性20/20；完整npm test exit0（legacy、calendar9、advisory47、fixpack4、C2五項全過）。乾淨基線套patch後build的HTML／Worker雜湊與受測版本一致。
- 四檔相同凍結輸入：40個Gate完整物件、scoring、VETO、adaptiveRating／風險許可、primaryValuation均不變。重播仍有證據缺項，信心均低，未宣稱來源全齊。
- 本機完成≠已上線。**正式站仍為v231；本輪未部署，需擁有者另行授權。** 四公司指引比較面板仍暫緩。

每項紀錄與首次失敗均已保留在報告連結。公開檔案不含私人存取入口、憑證或Tiingo原始價格。

---

# 最新：2026-10-21 修正包＋C2 已部署 v231，部署後驗收完成

擁有者已直接授權；按 Claude 07:45 部署條件執行。原生部署 succeeded，正式版本 **v231**，**v230 保留回滾**。正式站仍為擁有者私人存取，未擴大本次授權範圍。

## 部署與雜湊

乾淨基線 `f9c5f15b371de58d0a06ef5251ce5c8a895f217e` → fixpack.patch → build → c2.patch → build；部署前重新完整 `npm test` exit 0，全部 legacy、calendar 9、advisory 38、fixpack 4、C2 5 項通過，fail 0。git diff --check 通過。

發布來源：`6b924076503a47e346a3d72ff3efeb5260a8078f`。部署時間 2026-10-21 13:00 台北；最後獨立股指讀回 13:11 台北。

|項目|核對相符的 SHA-256|
|---|---|
|fixpack.patch|d69ac5bb2538c9b3115306eb8c490077797b284a69e9c07151dbcf560bae6d0c|
|c2.patch|9ad8c47bae31fa31008f88895b8a40e3f46fbf9ec6d94f505c6215dd69ad34e4|
|HTML／正式首頁讀回|93d22d219109e52161e0e85ab926ad86dab6fadfc5083c57144e5c21b1f9e638|
|Worker／上傳包內 Worker|613ac53005c0346259bf4aff78f95e18ced8c4c29a81f1d964ff9b4a56e79675|

完整 diff：[fixpack.patch](fixpack-20261021/fixpack.patch)、[c2.patch](c2-20261021/c2.patch)；生成 Worker 按 build 重建，不再次公開含私人操作說明的編譯上下文。[本輪完整 npm test 輸出](fixpack-20261021/deployment-npm-test.log) 已上傳並讀回比對，內容完全一致。

## 正式讀回

- 核心 **55/55**、市場／貴金屬 **36/36**、擴展 **12/12**。原核心65列含10個重複id；已固定為55個不同指標，缺值不消失。
- B1：主總經與獨立股指均通過。獨立股指舊15分鐘持久快取自然到期後，3/3均以10/20對10/19：SP500 **+0.283978%**、DJIA **+1.019608%**、NASDAQ **−0.022966%**。能源10/14對10/13：WTI **+1.041047%**、Henry Hub **+2.547771%**；比較起訖均保存。
- 融資／融券：官方10/20報表重抓、匯入及讀回成功；10/19 **final** 融資6406.17928億元、融券201911張；10/20 **provisional** 融資6381.00111億元、融券215912張。修訂book9筆包含初建，不宣稱9筆全為舊值更正；歷史同日市值分母缺失時不造比率。
- B2：正式HTML早晚標示06:30／22:30；實際市場回應代入共同金銀快照後，卡片與比值operands、時間皆相同。板塊獨立API為Tiingo主要來源adjClose、10/20、11/11，新增分數貢獻仍0。
- 本輪即時總經 **US59→64、TW58→60**。美股動能45→62.5；資料同時更新造成成長75→72、台股本土41→49.375。與原凍結資料US65／TW59分開列示；沒有改公式、權重或門檻。

|股票|正式站 C2 結果|最大／最小 EPS|風險許可|
|---|---|---:|---|
|8299|未評（估值分歧）|10.69153846|not_cleared|
|5289|未評（估值分歧）|14.63234871|not_cleared|
|2404|未評（估值分歧）|3.11795113|not_cleared|
|5009|C／保守觀察|1.51713919|not_cleared|

第一輪的過期／群聯FinMind402失敗紀錄已保留。群聯用既有refresh端點重試一次後成功，擷取時間05:06:18 UTC；其39／206.883／220.20／416.97四個EPS均可核對，沒有補造舊資料。

**同一批新輸入的控制組**：v230對v231，40個Gate狀態、四檔scoring及VETO物件完全相同；只有核准的三檔D→未評、5009 C→C。風險許可均not_cleared。[同資料比較](fixpack-20261021/identical-live-inputs-comparison.json)。

**真實時間的前後比較**則有過期轉有效等Gate變化，不能宣稱實際40格完全不變；已在完整報告逐格列出，所有總經／市場／擴展／股指列的status、is_stale、reason變化亦已逐列保存。

## 仍保留的 partial 與限制

全站run `0bacb91f-9834-4bcf-9eef-bdfc6a9872b7` 已完成 **partial**，匹配runId歷史已讀回。當輪板塊模組逾時；稍後獨立讀回恢復Tiingo 11/11，沒有倒改原run為全成功。

Gate4／5／8缺口仍在；群聯Gate6 **CFO／淨利−0.17倍、FCF−141.57億元**警訊保留。四檔VETO皆pending，仍各4條未知，風險預算未放寬。D1表格檢視器遇大型cache列的顯示限制，沒有宣稱直接讀到完整revision book；採匯入狀態與市場final歷史點交叉讀回。隔日修訂持續性待後續實際交易日觀察。

未發現未處理Worker exception或整體故障，未啟用回滾。未部署其他待辦、回測門檻或新計分。未把Tiingo原始價格、憑證或私人網站入口寫進公開紀錄。

[完整部署報告（含40個Gate及每列status變化）](fixpack-20261021/deployment-report.md) · [完整實際前後差異 JSON](fixpack-20261021/deployment-live-comparison.json) · [讀回與保存證據](fixpack-20261021/deployment-readback.json)。

每步checkpoint已保存：deployment-01-preflight 至 deployment-06-four-models；失敗及恢復過程可追溯。修正包與C2程式部署驗收完成，不代表整站所有資料／研究Gate均已通過。


## v231後剩餘工作盤點

[未完成工作與性質分類](remaining-work-20261021.md)：Gate8同業0/3及2027覆蓋、Gate4 3/10、Gate5B 0/8、C1／C3／C4、整體總經回測與持股門檻、新股自動蒐證、來源治理及跨日驗證。此為盤點，不代表新增修改或部署授權；Gate6真實警訊不列為程式待修。


## 現成成果與下次上線準備度

[準備度核對](ready-for-next-release-20261021.md)：本輪實讀四家官方財測檔，3034／5347各14季、3711／5274各4季，共36季預驗證研究證據，gate_impact均none；可優先接成證據面板，仍需網站匯入接線與測試，不自動通過Gate。均線、營收／EPS創高、PBR等顯示已在v231；C1／C3／C4尚非另一份完整待發布補丁。


## 擁有者最新決定：財測對照面板暫緩

使用者回覆「這個暫時不需要」。上一則提出的3034／5347／3711／5274官方財測對照／證據面板先暫緩；保留資料及核對紀錄，暫不整合、開發或部署。現有v231維持不變。準備度文件已同步標示暫緩，供Claude接手時遵循。


## 使用者圖片四項進度核對（v231）

圖片所指為綜合判斷、金價／美元面板、持股比例、自動化與穩定性，四者均尚未完整交付；與已暫緩的四家公司官方財測對照面板分開管理。本次僅核對狀態，沒有新增程式修改或部署。

|項目|已完成|尚未完成／驗證|
|---|---|---|
|綜合判斷|規則式草案結論、既有警訊、C2估值分歧、一般改判條件|信心高／中／低、估值／線型／大盤完整理由與具體改判條件尚未完整依指定格式完成。讀回approved=false、activeScoreContribution=0。|
|金價／美元面板|即時觀測來源、金銀同一快照核對、既有零軸演算法|金價1／5／20日變化與主面板尚未完成；DTWEXAFEGS新口徑與完整美元零軸表未接妥。本輪保存的dollarZeroAxis與goldZeroAxis皆insufficient，原因SOURCE_MISSING_STALE_OR_NOT_ALIGNED。|
|持股比例|草案框架、部分第28／29輪回測|整體總經分數歷史回測、極端門檻、持股降幅未完成核准；目前holding.policy_pending、suggestedRange=null，沒有實際輸出持股建議。|
|自動化與穩定性|整站更新入口、快取、巡檢歷史與匹配runId保存、官方融資最終值修訂流程|新股票自動蒐證未完成；本輪板塊主巡檢曾逾時、後續獨立讀取恢復，仍需排查及連續跨日驗證；融資隔日修訂持續性尚待實際下一交易日確認。|

v231發布成功與以上四項完整交付是不同驗收範圍；既有報告的partial與保留警訊不變。
