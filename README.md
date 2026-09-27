# 台股 Master Model 外部快照更新器

此套件提供 GitHub Actions 定時抓取、官方數據校驗及 Cloudflare Workers KV 快照寫入。前端快照結構以 `indicators` 為主，保存觀測日期、來源、計算口徑、狀態及失敗原因。GitHub-hosted runner 使用的出口網段會變動；外部執行可避開 Cloudflare Worker 的出口 IP，但不能保證所有上游 WAF 都會放行。

## 已納入

- FRED 官方 API：SOFR、一般臨時公開市場 Repo、ON RRP、非農月增（PAYEMS 相鄰月份差）、失業率、Sahm Rule、零售銷售 MoM、10Y-2Y、10 年實質利率、5 年 breakeven。
- 台灣官方來源：經濟部外銷訂單（美元單月 YoY）、國發會燈號；TPEx 上櫃漲跌家數使用櫃買中心 OpenAPI。
- 零是有效數值；`.`、空值、非數字才算缺失。
- 任一來源失敗時，各欄位獨立處理；沿用前次值並標記 `stale`。新觀測日期早於快照時拒絕倒退覆蓋。
- 沒有任何可用新觀測或可保留舊值時停止發布，避免整份 KV 快照被空資料蓋掉；全部來源失敗但有舊值時會發布 stale 標記。

## 指標定義

`RPONTSYD` 是 Fed 在臨時公開市場操作中的 Treasury 證券 Repo 承作額，不能解讀成單獨的 Standing Repo Facility（SRF）。它以 `REPO_TEMPORARY_OPERATIONS` 發布。`RRPONTSYD` 是 ON RRP。SRF 目前不以此序列替代，若需要 SRF 專屬金額，須另接 NY Fed 的 SRF 專屬結果。

## GitHub Secrets

在倉庫的 Actions secrets 設定：

- `FRED_API_KEY`
- `CF_ACCOUNT_ID`
- `CF_KV_NAMESPACE_ID`
- `CF_API_TOKEN`：僅需該 Cloudflare 帳戶的 Workers KV 讀寫權限。

工作流程每 6 小時執行一次，也可手動執行。缺少 FRED 金鑰時，美國序列會標成缺值／保留舊值；台灣官方來源仍會獨立更新。缺少 Cloudflare 寫入 Secrets 時不會寫入 KV。

## Worker 讀取契約

KV binding 名稱設定為 `MACRO_KV`，key 為 `market_snapshot`。`worker/read_macro_snapshot.js` 提供純讀取轉換器；讀不到 KV 時回報快照尚未初始化，不會即時回抓外部來源，也不會把 stale/missing 當作最新值。此 adapter 適用於可自行管理 KV binding 的 Cloudflare Worker。目前受管理的 Sites 部署流程未提供任意 KV 綁定設定，僅在本地新增 wrangler.toml 不會替既有 Site 完成綁定。需先確認平台支援的儲存／接入方式，或另建使用者自行管理的 Worker；不可直接替換現有 Site 的完整 API。

## 驗證

```sh
python -m unittest discover -s tests -v
python -m py_compile scripts/sync_macro.py
```

本地測試只使用固定測試資料，不會發出上游請求或寫入 KV。

## 首次驗收與範圍

此套件目前提供 13 項指標，不涵蓋現有網站全部指標、CPI/PCE、IORB、初領／續領、完整台股市場資料與模型重算。`complete` 只表示本份快照欄位完整，不表示整站完成驗收。

1. 手動 Run workflow 預設 `dry_run=true`：抓取及驗證，不讀寫 Cloudflare KV。全綠只表示腳本完成，仍須檢查 JSON 的 coverage、各欄位 status/date/error；partial 不等於資料全數成功。
2. 測試舊值繼承可本地執行 `python scripts/sync_macro.py --dry-run --previous prior_snapshot.json`。測試底本不可用於正式發布。
3. 確認真實資料與儲存目標後，手動取消 dry_run 才會讀取遠端底本並寫入 KV。排程採正式發布模式。
4. workflow 僅需 `contents: read`，不必提高整個倉庫的預設 token 權限。Cloudflare 權限由獨立的 CF_API_TOKEN 提供。
5. 來源失敗保留原值、觀測日期、last_success，更新 last_attempt 與 stale 狀態；未在本轮更新的既有欄位亦保留。零值有效。
6. 未經實測的 data.gov.tw 下載連結不視為獨立備援；若仍指向同一 TPEx 主機，不能消除同一上游故障。更換出口或 User-Agent 亦不保證放行。

所有測試資料（包括 71.35）僅用於解析回歸測試，不會填入正式快照。正式輸出均由當次來源取得或繼承有來源日期的舊值。

## 獨立 API Worker（方案 B，尚未部署）

`api-worker/index.mjs` 提供 `GET /api/market-snapshot`，只讀 KV、不連外部來源。缺少綁定／快照時回傳 503；部分數據有效時回傳 partial 與逐項缺值。即使 ETL 停跑，讀取端仍會將超過 36 小時未更新的快照標舊，避免永久顯示最新。

在使用者自己的 Cloudflare 帳戶中，於 api-worker 目錄複製 wrangler.toml.example 為 wrangler.toml，填入實際 namespace ID，再透過 Wrangler 設定 `SNAPSHOT_READ_TOKEN` Secret 並部署。這是獨立 Worker，不能將上述指令套在受管理 Sites checkout 上。

此端點預設要求 `Authorization: Bearer <SNAPSHOT_READ_TOKEN>`，不提供匿名存取或跨域瀏覽器直連。將讀取 Token 儲存於 Sites 的 Secret，由 Sites 伺服器呼叫此端點；不得把 Token 寫入前端 JavaScript。Sites 伺服器仍有一次對中繼 API 的連線，不能稱作零外部相依性。待真實 API URL、讀取 Token 與完整資料合併驗收完成，才接入現有網站。

沿用 schema_version=1、既有大寫指標鍵及 ok/stale/missing，避免另創 live 與小寫鍵造成讀寫不相容。零售採 RSAFS（含餐飲），不改成 RSXFS（不含餐飲）。coverage.total=13 只代表此端點規劃項目數；不硬寫整站 52 或宣稱全覆蓋。

驗證：`node tests/test_api_worker.mjs`。單元測試不等同 Cloudflare 線上驗收。
