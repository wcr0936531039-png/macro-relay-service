# 第二項：正式保存驗收通過後，已恢復原排程

同一批新正式讀回資料，v231來源對v232已部署來源的控制比較：四檔40 Gate完整物件、scoring、VETO、adaptiveRating及primaryValuation全部相同，風險許可仍not_cleared。不是宣稱不同時間市場資料完全不變。

原有「台股整站每日巡檢」已啟用；Sites關聯排程與Automations peek均讀回is_enabled:true，原Asia/Taipei每日06:30／22:30不變，沒有另建重複任務。工具next_run_time仍null，故不宣稱下一次已觸發或已完成；保存的RRULE與啟用狀態已確認。

提示已更新並讀回完全相符：同服務身分每10秒接續checkpoint；啟動409及保存503有限重試；核對匹配history與四檔audit；早上採market-only＋保存的macro_morning包裝，禁止含信用的預設收集；晚間若提早啟動，等實際22:30後才macro-only／statistics-only。每輪持續寫diagnostics，不公開憑證或Tiingo價格。

本次正式run為partial且四檔audit4／4保存，來源缺口照實保留。晚上實際新信用捕獲／翌晨跨日保持仍待未來排程驗證，沒有以本機測試預支完成。v231保留回滾。
