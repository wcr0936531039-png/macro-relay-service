# 修正包本機驗證中：未部署，C2未套用

目前程式已先保存至 [fixpack-checkpoint.patch](fixpack-20261021/fixpack-checkpoint.patch)。
SHA-256：`efabb7006bddb3e327fcd027d3b4f72ce7e04c018df4656d5a7b7f2e2c77cf46`。
Git blob已讀回核對：`2a688b647cfb7b73c4041657f632591c3144347e`。
基線為已發布整合版來源 f9c5f15b371de58d0a06ef5251ce5c8a895f217e。只含固定目錄／融資最終值／B1／B2；沒有C2或回測新增計分。

完整npm test重新執行中；先前執行未留下可核對的退出狀態，因此不宣稱通過。完成修正包報告後才套C2，最後另請擁有者授權部署。此前正式站v230不變。

已保存初步發現與凍結資料比較：[02-data-fixes-checkpoint.md](fixpack-20261021/02-data-fixes-checkpoint.md)。正式65列含10個重複id，核心實際55個指標；不湊數，市場固定36。US59→65、TW58→59是單日變化修正的本機重播，非正式站已變動。最終報告會附完整比較與測試結果。
