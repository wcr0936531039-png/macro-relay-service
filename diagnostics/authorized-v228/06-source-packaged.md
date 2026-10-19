# 06 已封裝並推送精確網站來源

Sites官方source helper成功回傳並結束exit0；工作目錄clean。

project_id：`appgprj_6ab2cc2055ac8191a2244d934f7384ee`
source commit：`543793fa6be1a9d4dfde79d0be4313eeb436f8e8`
archive：`v228-authorized-patch-20261020.tar.gz`

完整測試與diff check均在該內容上通過；後續沒有更動原始碼。接著用此commit與其匹配archive執行owner-private正式部署，保留原網站ID與私人存取。

部署前正式API讀回（21:33Z）：DEXJPUS status ok仍帶過期reason；JPY_HV20/HV60均stale，值5.804832905239327／9.756886685658461，觀測日10/9。這份實際前狀態會與部署後讀回分開保存，不把不同來源更新當作同一份固定輸入比較。