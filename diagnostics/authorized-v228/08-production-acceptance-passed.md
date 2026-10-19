# 08 正式部署驗收完成

平台v229（v228修補版）與原網站URL相同，存取仍只有擁有者。

| 驗收 | 實際結果 |
|---|---|
| 完整macro-market | HTTP200、36列；只有JPY_HV20/60由stale→ok，兩列及DEXJPUS reason均null；值與10/9觀測日不變 |
| 美股板塊 | HTTP200、OK、來源12代號／板塊11/11，資料池最新10/19 |
| 四檔Master | 8299、2404、5289、5009均HTTP200，板塊子模組OK；整體degraded依舊 |
| 群聯Gate2 | evaluated，共同最新交易日判讀 |
| 群聯Gate4 | 年報證據已顯示，仍warning；沒有製造分數 |
| 群聯Gate5 | 季度財測not_applicable／structural_unavailable；Gate5仍partial，surprise0/8 |
| 群聯Gate8 | Yahoo2027人數12，productionEligible:false，不借給FactSet；Gate8仍partial |
| 群聯Gate6 | warning保留，CFO/淨利−0.17倍、FCF−141.57億元 |

前後完整觀測、正式面板必要欄位與機器驗收摘要已上傳artifacts。其他未授權項目未擴充。

source commit `543793fa6be1a9d4dfde79d0be4313eeb436f8e8`；部署ID `appgdep_6ad68d37e31c8191b1f2435d34c8c780`；version_id `appgprj_6ab2cc2055ac8191a2244d934f7384ee~appgver_f8cc8799fc688191b5953b51abf844be`。