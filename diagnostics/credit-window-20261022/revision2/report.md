> 後續檢查更正：本機合成案例已重現觀測日陳舊仍列snapshot、缺餘額仍列snapshot兩個未涵蓋漏洞；另發現巡檢保存失敗未上拋。既有11項與全測試通過紀錄保留，但本patch目前不具直接部署準備度，先補修N01／N02與回歸測試。[完整問題清單及反例](../../issue-inventory-20261023/report.md)。未部署。

# 信用時間閘門修補 revision2：本機完成，未部署

## 範圍與結果

以正式 v231 來源 `6b924076503a47e346a3d72ff3efeb5260a8078f` 為乾淨基線。官方大盤信用備援及個股 FinMind 融資融券均加入台北時間 22:30 閘門；22:30 前不新抓信用，保留既有觀測日、原擷取時間與來源。成交值、法人等非信用資料不受此閘門阻擋。

大盤保留七個信用指標目錄；無有效歷史時明確 missing，過期為 stale，不新造觀測。個股新增獨立持久快取 stock-credit:v1:<代號>，晚間成功抓取才保存，上午只讀。個股融資日期、擷取時間、延後狀態分開呈現，不能借用法人日期。拒收代號不符、未來日期及不合時段的個股快照。

首次部署後、尚未累積獨立晚間個股快照時，上午會顯示 deferred／缺值；不能從舊混合快取推定其信用擷取時間。快取保存失敗明確回報 error；沒有擴大風險許可或修改 Gate 門檻。

## 驗收

- 新增 11 項測試全過，fail 0。
- 完整 npm test exit 0；legacy、calendar 9、advisory 38、fixpack 4、C2 5、credit-window 11 全通過。各組詳見完整日誌；不把舊測試名稱中的 live 字樣當成本輪正式站驗收。
- git diff --check 通過。新乾淨 worktree 套本完整 patch，npm run build exit 0；Worker SHA 與受測版本一致。
- Patch SHA-256：`d8641baf67ed1e75910b24dfcad7612d6a1d33a5d2ce3bc5abcddf82dcbf7b4c`。
- HTML SHA-256：`93d22d219109e52161e0e85ab926ad86dab6fadfc5083c57144e5c21b1f9e638`，未變。
- Worker SHA-256：`a5b2d79df69bef42080420e14a1513e83fd5d98a60a65b54415881c7ef2b79f8`。
- 四檔凍結輸入（8299、5289、2404、5009）比較：40 Gate 完整物件、scoring、VETO、adaptiveRating／風險許可、primaryValuation 均不變。三檔仍未評（估值分歧），5009 仍 C／保守觀察，四檔風險許可 not_cleared。
- 合成時鐘案例（非即時行情）：上午官方信用請求 3→0，個股信用請求 1→0；完整七列及個股 marketActivity／datasetStatus 前後值在 before-after.json。數值變化是測試來源與保存快照不同，不能引用為市場變動。
- 初次 revision2 測試曾因 fixture 語法、財報測試直接 import 遺漏共用 helper 失敗；已修正 fixture，財報測試改用實際 build 產物並固定晚間時鐘，單項及全套重跑通過。revision1 檔案保留，不覆蓋為本版。

## 接手與邊界

本 patch 是從乾淨 v231 產生的完整修補，取代 revision1；不要疊套兩版。C1 修訂2獨立待審，不包含在此 patch。公開 patch 只含來源、測試與 package；生成 Worker 請 build 重建，避免公開私人操作上下文。compare-local.mjs 是本機重播工具，其路徑需按接手環境調整；所用凍結私人輸入不公開。

**正式站仍 v231，本輪未部署。原排程保持暫停。** 本機通過不代表正式站上午已受限，也不代表整站巡檢完成。

背景整站 run 的 waitUntil 任務遭平台時限取消仍未修復；FRED 維護造成來源缺項仍保留。首次 run 無 completedAt，第二次 run 的完成與歷史沒有驗收。自動核准曾拒絕第二次巡檢輪詢，原因是正式站上午仍抓信用；沒有繞過限制。部署本 patch 後仍需獨立處理背景任務分段／可恢復執行，再核對匹配 runId、completedAt 和持久歷史。

尚需擁有者審查及部署授權；未恢復排程，未自動通過任何研究 Gate。
