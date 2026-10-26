# 2026-10-26 v235 hotfix 驗收
結果：v236 已部署；①③ PASS、② FAIL、④有資料時效差異；每日巡檢保持停用。
基線 v235：4ac4af9f0817c40a135c8e1b1df3603569726b1b，保留回滾。
Patch SHA256：c46c98406536419d722bbdb20a73a1ba844545edce56624b11b5a816317911ac
dist/index.html SHA256：2d51dc256651a1afac37dc26388aec909dbd29301f0530edd006cb2e44534f92
部署來源：88f5f89c109a63cc38f76593341d1f3a463daa57；單次部署 succeeded。
git apply、node build.mjs 成功；TZ=UTC npm test exit 0，新增 test:v235-hotfix 2/2。
手動收集使用新版官方工具；行情最新10/22，72個交易日，1947/1985檔，未補造缺值。
九序列含DTWEXAFEGS、CPI、八組來源94筆與公告均匯入ok:true，完成讀回。
晨間略過信用收集，沒有本輪statistics.json；沒有把舊觀測改成新日期。
巡檢runId：698b8754-3a13-4f65-bc4a-b05d8575f542。
完成：2026-10-26T00:08:02.715Z（台北08:08）；status=partial。
history同runId／完成時間相符，gateAuditCount=4。
① PASS：8299／5289／2404／5009 均recorded:true，沒有step_timeout；上輪為0/4。
② FAIL：巡檢後8299仍status=insufficient、reason=CB_REGISTRY_STILL_LOADING、scoreContribution=0。
兩次正式讀回generatedAt：00:08:34.826Z、00:09:39.541Z，皆相同失敗碼；非只看第一次冷快取。
未讀得三券、群聯三目前2468.8及海外兩券標示，故不宣稱可轉債完成。
③ PASS：TW_EXPORT_ORDERS=49.68、2026-08-01、status=ok、source=data.gov.tw/dataset/6099。
scoring=pending_threshold_approval；未計分；已不再讀經濟部62.36舊快照。
④ 2404／8299／5009的評級、各Gate狀態與風險許可均與本輪部署前v235讀回相同；5009仍degraded／C。
5289 blocked→valuation_divergence；Gate4／6 blocked→warning、7／10 blocked→evaluated、9 blocked→partial。
5289 stockCheckedAt由10/25 17:14:15.691Z→10/26 00:01:46.137Z；原過期財報快照刷新後參與判讀，數值與現金流警訊保留。
四檔riskPermission仍not_cleared，Gate5／8未自動通過；未新增評級或風險權重。
其他來源：總經ok55/55、擴展partial11/12（M1B−M2待核）、市場／貴金屬pending36/36。
美股指數ok3/3、跨市場ok4/4、板塊ok11/11、公告ok3/3；既有來源缺口不冒稱已修。
待查推論：attachPanelSources回傳讀取中後，背景收集是否獲ctx.waitUntil保活；本輪未擅自修改或追加部署。
恢復判定：①～③未全通過（②未過），未啟用每日巡檢；Sites最終讀回仍is_enabled=false。
憑證每次由get_site取得、只經隱藏stdin使用，未輸出或存檔；未開始排隊功能。
