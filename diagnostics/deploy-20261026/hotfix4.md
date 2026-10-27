# ⑥ G＋F2 驗收：v240 已部署，整體 partial（2026-10-27 台北）

- G patch SHA-256：564ccd5e02d74901007d8c8c41f146f8eecbeb79e22dee46ec044d89a3bf0fd6，核對通過。
- F2 patch SHA-256：3f4f587755179970fd58b828b9f62717f4c919fa687c2c336737a5774ae4f73a，核對通過；未套舊 F。
- G：git am、Python 35/35、既有 Node 與板塊 Python 20/20 通過；main=e3ea733057d3a02f841719886452dd22c7245482；Actions 40411786978 success；DTWEXAFEGS ok／40筆／最新2026-10-23。
- F2：乾淨 v239 e954f6b 套用、build、完整 TZ=UTC npm test exit 0（含新增4項）；來源 d871583e591660ae042d088d11c225aee12583c3；15:42部署一次為v240，v239保留回滾；HTML SHA-256=05c731ec5cece149e4c68daa25f7906b029bec17f0fc4455da25d0c13e874334。
- 美元實際畫面：8299零軸−40.62、有圖，來源 official_import（FRED DTWEXAFEGS；時點可用觀測10/19）；中繼備援／過期拒用由測試通過，未刪除有效匯入強迫備援。
- CB實際畫面：「櫃買清單、觀測站月報：網站直連失敗，改用 GitHub 排程代抓的同一份官方檔（保存SHA-256）」；3券、群聯三目前轉換價2,468.8不變。
- 新版收集／匯入：官方9序列接受，IORB最新10/27≤UTC今天10/27，無invalid_series_history；CPI同月同值338.896；行情10/27、1957/1985、73交易日；下午未抓信用。
- 舊快取：8299／5289／2404／5009／2330於07:43Z首開、07:44Z再開，五檔已換新快照、exRightsEvents各4／2／2／2／8筆且股利來源ok；舊快取缺除權息註記消失。
- 5009：10/27實際畫面排列強、還原MA120=33.653092；進場仍觀望（技術均線分數0，未達+3），續抱、還原MA20=33.275；不同於10/22預期樣本，不強改可進場。
- 10/27出場讀回：8299／5289／2404均exit，還原MA20各2011.75／1211.5／1206.5；2330 exit、MA20=2482.25；未顯示舊快取警告。
- 五檔最終評級與riskBudget均同部署前（5009仍C、其餘仍未評）；但Gate9：8299 conditional→not_applicable、5289 partial→blocked、5009 conditional→not_applicable，其餘Gate狀態相同，故「所有Gate不變」驗收未通過。
- 原因：三檔上櫃官方發行股數本輪TPEx逾時而缺值，替代估值同日驗證不足；5289明列缺股數。5009估值子級B→B+、最終仍C；行情10/22→10/27。既有發行人快取在上市資料成功時保留24h，可能延長上櫃缺值；本輪未另改程式／規則。
- 每日巡檢is_enabled=true、06:30／22:30；最新實際排程recorded_status=no_update，無新網站run可對照，尚未通過恢復後實跑驗收；已另存patrol-enabled.md，不用01:07手動partial冒充。
