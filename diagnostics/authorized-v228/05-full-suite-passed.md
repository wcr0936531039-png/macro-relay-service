# 05 部署前全套測試通過

build成功；完整npm test退出碼0，包含新增精確A1文案回歸、A2八項NYSE案例、群聯面板、所有既有Gate/VETO、來源隔離及UI契約。git diff --check通過。

已重新執行完整36列同資料重播：值、日期、順序全部不變，status改變仍只有JPY_HV20/60 stale→ok；其他變化為is_stale明確化及精確過期reason清除。

最終完整diff：`diagnostics/artifacts/v228-20261020-authorized-site.diff`。
完整測試日誌：`diagnostics/artifacts/v228-20261020-authorized-site-test.log`。

測試中的故障注入403/503與既有Node/npm警告不是正式站抓取結果；全套exit0。接著封裝與部署既有v228修補，平台新存檔版本會依平台編號，不覆寫舊版本。