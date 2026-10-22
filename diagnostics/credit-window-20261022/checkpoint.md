# 2026-10-22 本機信用時間閘門第一版檢查點

來源基線v231（6b92407）。官方MI_MARGN／MI_MARGN_TREND／BFIJ3U三路於22:30前不抓取，保留原日期與核對時間。新增7/7測試通過，完整npm test exit0；另以預設連外回503的隔離環境跑全套，也exit0。原先5個反例在修補前全部失敗。

同凍結輸入四檔的40個Gate完整物件、scoring、VETO、adaptiveRating與primaryValuation均不變；比較資料明標本機重播，不是新正式站讀回。patch與SHA見manifest.json，完整測試及7列前後資料已保存。

續查發現：個股FinMind的TaiwanStockMarginPurchaseShortSale是另一條融資融券路徑，第一版只處理官方大盤信用端點，因此不能宣稱所有信用抓取都受限。正在另補個股路徑，將另存revision2，不覆蓋本檢查點。正式站仍v231，未部署；巡檢排程保持暫停。背景waitUntil取消問題另列待修，不能宣稱已修好。
