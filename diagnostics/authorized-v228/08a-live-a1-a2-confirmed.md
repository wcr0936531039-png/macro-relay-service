# 08a 正式A1/A2讀回通過

部署後正式GET `/api/macro-market` HTTP200，完整36列已保存：

| 指標 | 部署前 | 部署後 | 值／日期 |
|---|---|---|---|
| DEXJPUS | ok，帶「資料較舊」reason | ok，reason:null | 158.34／10/9不變 |
| JPY_HV20 | stale，帶自生過期文案 | ok、reason:null、derivedFrom:DEXJPUS | 5.804832905239327／10/9不變 |
| JPY_HV60 | stale，帶自生過期文案 | ok、reason:null、derivedFrom:DEXJPUS | 9.756886685658461／10/9不變 |

沒有把舊觀測日改成新日期；依母序列已驗證發布窗恢復有效。這兩列重新納入既有模型，擁有者已知。

正式`/api/us-sector-report?refresh=1` HTTP200、OK、11/11、資料池10/19。群聯Master板塊也OK；其整體仍degraded，其他Gate限制未解除。

正在讀完其餘三檔Master與保存完整部署驗收。