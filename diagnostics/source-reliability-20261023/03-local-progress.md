# 本機修補與真來源收集進展

Tiingo改每次最多1個新請求、每檔D1保存，未嘗試檔不覆寫為失敗；原22檔、adjClose、交易日檢查、額度guard與Yahoo獨立備援保留。pending分批不套來源失敗的一小時冷卻；同runId／同module checkpoint接續，最多30次後明確列partial並繼續其他保存。單步板塊預算16秒，仍低於25秒租約；不是單純把整輪timeout拉長。

新增分批與來源測試，加既有恢復測試共19項已通過。首次2項pending測試失敗是測試注入字串被前一行註解吃掉，已補換行再跑；保留此定位，不改正式判定或刪斷言。完整npm test正在執行，尚未宣稱全套通過。

真來源收集8/8成功、275筆、errors0。consumer已由0變5筆，RSS HTTP200但empty_report_feed的失敗與官方分類HTML HTTP200備援成功均保存；原始發布日保留，read_state=category_excerpt，沒有冒稱讀過全文或通過Gate。半導體10筆；twse119、tpex64、display10、energy10、steel7、aviation50。

外部匯入增加來源模式標記與原始擷取時效核驗；強制重建個股池可使用6小時內有效外部匯入，不被多餘Worker403降成過期；過時／空報告仍拒用，原日期不更新。尚未部署／尚未匯入正式站這275筆。

MOEA月表／圖表／新聞／首頁403已保存；官方data.gov下載指向同一主機CSV，官方PDF備援也在測試。沒有用搜尋摘要或舊值假裝新取得原始檔。真實晚間與翌晨信用保持待驗。
