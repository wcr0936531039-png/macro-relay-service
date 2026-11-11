# hotfix13（2026-11-11）
- 授權：中繼 U-6、網站 v255＋v256 一次部署、驗證後精簡巡檢指令；11/08 後缺漏巡檢不補做。
- 中繼 U-6：GitHub 連接器已推 main；commit 183aa79、49ba865；blob scripts/sync_keyless.py=48aba82986a7a6a3bfa12fa9be8606c5086b23ef，tests/test_keyless.py=482a09b57372fe8c05e88bfd8c65c9f3d936ef67，皆吻合；本輪未跑測試。
- 網站：v255／v256完整patch SHA吻合；build完成，TZ=UTC npm test exit 0（末組94/94）；匿名後台SHA e5d736dc7c026c2768147d4f5256dbd52917ac92b634b97c18a0ccafaf11cd42吻合，待一次部署。
- 部署：source 4c8f2b91b23a442495a295fb3014aa7e026f1e41，v255＋v256一次部署succeeded；原3785fe0留回滾；正式後台SHA 5ba180e37875cbc712df6993b7628245d9fbd4069b5209465e5c71c975bed112。
- compact驗證HTTP200、compact:true、1073字元；精簡巡檢指令已更新（保留存取段）；06:30／22:30時段及enabled=true完全不變。
