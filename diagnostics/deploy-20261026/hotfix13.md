# hotfix13（2026-11-11）
- 授權：中繼 U-6、網站 v255＋v256 一次部署、驗證後精簡巡檢指令；11/08 後缺漏巡檢不補做。
- 中繼 U-6：GitHub 連接器已推 main；commit 183aa79、49ba865；blob scripts/sync_keyless.py=48aba82986a7a6a3bfa12fa9be8606c5086b23ef，tests/test_keyless.py=482a09b57372fe8c05e88bfd8c65c9f3d936ef67，皆吻合；本輪未跑測試。
- 網站準備：v254乾淨基線3785fe0；v255 SHA 20fc9d2e…、v256 SHA 979bdf66…完整吻合，依序套用、build完成；完整測試執行中，尚未部署。
