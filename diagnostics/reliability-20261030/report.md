# 2026-10-30 已知問題處理

- 已開始，未部署新修補；正式最後確認為Sites v247（含交接v248）。
- SLOOS根因：七月調查仍為Fed索引最新一期，8/3發布，11/2 14:00美東排定下一次；通用120天觀測日規則在10/30誤判。將採可追溯官方發布驗證，不改觀測日、不補數值、不無限延長有效期。
- stepStatus根因：v244原設計保存更新前狀態（測試也明確要求pending）；將分離目前stepStatus與previousStepStatus，保留歷史過程，不冒充未完成已成功。
- 信用舊資料capturedAtBasis=verifiedAt是明示備援；不可事後製造獨立擷取時間。今晚取得新資料後才能驗新擷取及翌晨保留。
- FinMind名稱402、MOEA403、公告原始代碼、Gate4/5/8缺項、Gate6真實警訊、新股樣本暖機均仍保留；本輪先處理可自主驗證的根因。
- 官方證據：https://www.federalreserve.gov/data/sloos.htm；https://www.federalreserve.gov/newsevents/2026-november.htm。
