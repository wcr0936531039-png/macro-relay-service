# 2026-10-21 正式站部署前基線：既有資料缺口

目前仍是 v230，尚未發布修正包或 C2。

本輪真實 API 讀回與前次本機凍結資料驗收不同，必須分開看：

- 四檔 Master（8299、5289、2404、5009）HTTP 200，但 `status=blocked`、`adaptiveRating.status=data_unavailable`、`grade=null`；四檔 `riskPermission=not_cleared`。
- 群聯 Gate 7 出現 FinMind 免費 API HTTP 402（Requests reach the upper limit），股票股利／分割／面額變更資料不完整；財報必要欄位亦有缺項。
- 其餘三檔多項財報／估值／行情快照過期，Gate 7、9、10 blocked。不得延長舊快照效期或補造新擷取時間來湊成 C2 預期評級。
- Gate 2 四檔均 evaluated，官方交易／信用 9/9，觀測日 2026-10-20。
- Gate 3 四檔均 evaluated，全市場 1,953/1,983、70 個交易日。
- 總經 API 仍回傳 65 列、55 個不同 id；市場 36 列／36 個不同 id。
- B1 舊值仍可重現：10/19 SP500 −1.49%、10/14 WTI +7.25%、Henry Hub +1.9%，與修正包針對的錯誤一致。
- Tiingo 本輪 `TIINGO_LATEST_SESSION_MISSING`，已自動退至 Yahoo 並標備援來源，美股板塊 11/11；此亦先於本次部署發生。

部署後將以這份真實基線比較 Gate 和風險權限，同時另列已批准凍結資料的 C2 預期 8299／5289／2404 未評、5009 C。若缺失持續，不宣稱現行四檔評級驗收已通過。未擴大修改資料供應商或其他待辦。
