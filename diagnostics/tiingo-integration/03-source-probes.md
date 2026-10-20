# 第2步來源實測與缺口（2026-10-20；本機，未部署）

- TWSE `https://www.twse.com.tw/rwd/zh/marginTrading/TWT93U?date=20261019&response=json` HTTP200。
  - 回應標題「信用額度總量管制餘額表」，單位「股」。欄位重名，必須使用 groups[2]「借券賣出」區塊及欄位12「當日餘額」，不能誤用欄位6的融券今日餘額。
- TPEx Swagger 實測確認 `/tpex_margin_sbl`；`https://www.tpex.org.tw/openapi/v1/tpex_margin_sbl` HTTP200。
  - 借券賣出欄位是 SecuritiesBorrowingBalanceOfTheMarketDay；不是 SaleBalanceOfTheMarketDay（融券）。ROC日期1151019轉2026-10-19。
- 官方公司名冊 TWSE JSON及TPEx CSV均HTTP200；產業別實際為代碼。2330=24、8299=24、5289=25、5009=10、2404=31；2882=17（金融）、2903=18（百貨）。
- FinMind 官方文件確認 EPS 已為單季，不能再做YTD差分：
  https://finmind.github.io/tutor/TaiwanMarket/Fundamental/
  PBR 為 TaiwanStockPER獨立欄位，虧損時不應因PER無效而丟失PBR樣本：
  https://finmind.github.io/tutor/TaiwanMarket/Technical/

## 已遇到、保留的缺口

- 為區分2404工程與一般其他電子，試讀官方公司主要業務頁：
  https://mopsov.twse.com.tw/mops/web/ajax_t05st03?encodeURIComponent=1&step=1&firstin=1&off=1&queryName=co_id&inpuType=co_id&co_id=2404
  本機HTTP503，未取得主要業務原文。僅靠代碼31會把工程誤配XLK；新映射採保守 ambiguous，待附日期/原文網址的業務證據才能改XLI，不寫死2404例外。
- 27通信設備/電信、23油氣/公用、14營建/工程也須業務證據；不猜測。
- 已存網站舊個股快照沒有PBR完整序列與EPS口徑欄位時，需下一次實際個股擷取才補得進；本機不寫回正式資料、不用假值填滿。

面板計算與完整測試仍在進行；此檔先保存實際來源障礙，供Claude接手。
