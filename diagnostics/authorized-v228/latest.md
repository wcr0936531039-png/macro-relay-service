# v228兩項授權：執行進度

依2026-10-20 05:32擁有者授權；其他項目不在本次範圍。

1. [授權範圍](01-scope.md)：已核對Claude blob4d122668及本對話授權。
2. [PR #6合併](02-pr6-merged.md)：已鎖定head2c098f9合併，commit835168c。
3. [A1精確回歸](03-a1-regression-fixed.md)：先重現reason矛盾、再修精確一行；目標測試已通過。
4. [合併後真實發布](04-postmerge-publisher-passed.md)：run39328238333 success，最新完成日檢查與Raw讀回均通過。

目前等待完整npm test結束，尚未部署網站。全套測試exit0後才使用Sites正式發布，並記錄版本／commit／部署ID及正式站讀回。

既有部署候選只包括A1＋A2＋已審閱群聯面板；A4–A6、B1–B8、R2–R5、P2/P3未擴充。