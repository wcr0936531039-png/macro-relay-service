# 03 A1部署前補件已修正

新增精確回歸案例：stale＋is_stale:true＋有效releaseVerification＋reason「官方觀測或最近來源核對已過有效期；等待更新。」。

先在舊bundle執行，確實失敗：status已ok，但reason仍為該過期文案，預期null。之後僅將這句加入obsoleteObservationReason清單，build成功、目標測試通過。沒有以一般清空reason掩蓋來源錯誤。

完整npm test正在執行；只有全套exit0才進入部署。沒有改動A4–A6、B1–B8或P2/P3。

PR #6合併後真實US Sector History run39328238333已success：Unit tests、Fetch market data、Validate coverage and freshness、pipeline、Commit snapshot與public Raw驗證全部通過。不是僅引用PR CI。