# 2026-10-30 已知問題處理

- 已開始，未部署新修補；正式最後確認為Sites v247（含交接v248）。
- SLOOS根因：七月調查仍為Fed索引最新一期，8/3發布，11/2 14:00美東排定下一次；通用120天觀測日規則在10/30誤判。將採可追溯官方發布驗證，不改觀測日、不補數值、不無限延長有效期。
- stepStatus根因：v244原設計保存更新前狀態（測試也明確要求pending）；將分離目前stepStatus與previousStepStatus，保留歷史過程，不冒充未完成已成功。
- 信用舊資料capturedAtBasis=verifiedAt是明示備援；不可事後製造獨立擷取時間。今晚取得新資料後才能驗新擷取及翌晨保留。
- FinMind名稱402、MOEA403、公告原始代碼、Gate4/5/8缺項、Gate6真實警訊、新股樣本暖機均仍保留；本輪先處理可自主驗證的根因。
- 官方證據：https://www.federalreserve.gov/data/sloos.htm；https://www.federalreserve.gov/newsevents/2026-november.htm。

## 本機修補與反例（已保存，完整測試中）
- 三項已實作：SLOOS官方發布窗／最新期核對、stepStatus與previousStepStatus分離、capturedAtBasis重讀不升級。
- 官方直抓日曆在本機403；使用已讀取的Fed官方索引、圖表與日曆核對本期0.0／8月3日發布／11月2日14:00 EST下一期。明確到期，不將今日當觀測日；後續季度須有新近官方最新期索引核對，否則不外推有效期。
- 15項針對性全部通過；第一次測試替身漏DB.run造成2項測試失敗，補正替身後通過，非正式站故障。
- 相同55列／相同時間前後比較：只SLOOS狀態與理由改變，日期、數值、擷取時間不變。stock由ok/pending改ok/ok，previousStepStatus=pending；信用備援依據維持verifiedAt，不再變capturedAt。
- [完整來源diff](source.patch)，SHA-256 1a644cfcf757435fd507f34ac677adf24b69e8b7b2a34642569ff8b9251067a5；[55列前後比較](before-after.json)。
- 尚未部署；完整測試執行期間新增兩項長期回歸測試，將對最終固定來源再跑完整npm test後才發布。
