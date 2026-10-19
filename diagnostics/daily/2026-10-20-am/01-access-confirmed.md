# 01 本輪資料巡檢開始

2026-10-20台北；本輪以正式網站v229資料介面執行。

Sites get_site已確認：current_user_role owner、custom政策僅owner、外部訪客0、群組0。服務憑證僅留記憶體並透過隱藏stdin使用，未存檔或輸出。

目前正在讀正式/api/official-data-tools的操作說明、收集器與匯入器，以及已保存market-scanner sessions；按>=60時僅收1個最新官方交易日，否則收60日。

只更新資料、保存巡檢，不修改網站程式或模型規則；來源失敗／缺值／過期如實保留。