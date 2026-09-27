// Pure KV read adapter. It intentionally performs no network requests.
const DEFINITIONS = {
  SOFR: ['SOFR', '擔保隔夜融資利率', '信用／融資', '%'],
  ON_RRP: ['RRPONTSYD', '紐約聯儲隔夜逆回購操作量', '信用／融資', '十億美元'],
  REPO_TEMPORARY_OPERATIONS: ['RPONTSYD', '紐約聯儲臨時公開市場 Repo 承作額（非 SRF 專屬）', '信用／融資', '十億美元'],
  NFP_CHANGE: ['PAYEMS', '非農新增就業（NFP）', '需求／就業', '千人'],
  UNRATE: ['UNRATE', '美國失業率', '需求／就業', '%'],
  SAHMREALTIME: ['SAHMREALTIME', 'Sahm Rule 官方指標', '需求／就業', '百分點'],
  RETAIL_SALES_MOM: ['RETAIL_SALES_MOM', '美國零售銷售 MoM（名目）', '需求／就業', '%'],
  T10Y2Y: ['T10Y2Y', '10Y−2Y 名目殖利率利差', '利率／政策路徑', '%'],
  DFII10: ['DFII10', '10 年實質殖利率', '利率／政策路徑', '%'],
  T5YIE: ['T5YIE', '5 年通膨 breakeven', '通膨／政策', '%'],
  TW_EXPORT_ORDERS: ['TW_EXPORT_ORDERS', '台灣外銷訂單年增率（美元）', '台灣景氣', '%'],
  TW_NDC_SIGNAL: ['TW_NDC_SIGNAL', '國發會景氣對策信號', '台灣景氣', '分'],
  TPEX_BREADTH: ['TPEX_BREADTH', '台股上櫃漲跌家數（TPEx）', '台股市場', '%'],
};

function hasNumber(value) {
  return typeof value !== 'boolean' && value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value));
}

export function validateSnapshot(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) throw new Error('快照根節點必須是物件');
  if (snapshot.schema_version !== 1 || !snapshot.indicators || typeof snapshot.indicators !== 'object' || Array.isArray(snapshot.indicators)) {
    throw new Error('快照 schema_version 或 indicators 格式不符');
  }
  return snapshot;
}

export function adaptSnapshotRows(snapshot) {
  validateSnapshot(snapshot);
  return Object.entries(DEFINITIONS).flatMap(([key, [id, name, group, unit]]) => {
    const item = snapshot.indicators[key];
    if (!item || !hasNumber(item.value) || !/^\d{4}-\d{2}-\d{2}$/.test(String(item.date || ''))) return [];
    const stale = item.status === 'stale' || item.is_stale === true;
    const row = {
      id, name, group, unit, value: Number(item.value), date: item.date,
      status: stale ? 'stale' : item.status === 'ok' ? 'ok' : 'missing',
      is_stale: stale, snapshot: true, provider: item.provider || '外部排程快照',
      source: item.source || null, method: item.method || null,
      reason: item.error || (stale ? '保留前次成功觀測；資料較舊' : null),
    };
    if (item.light) row.light = item.light;
    for (const field of ['advancers', 'decliners', 'prior_date', 'prior_value']) {
      if (item[field] !== undefined) row[field] = item[field];
    }
    return [row];
  });
}

export async function readMacroSnapshot(env) {
  const kv = env?.MACRO_KV;
  if (!kv || typeof kv.get !== 'function') throw new Error('MACRO_KV binding 尚未設定');
  const snapshot = await kv.get('market_snapshot', 'json');
  if (!snapshot) return { status: 'uninitialized', rows: [], reason: '快照尚未初始化；未對外部資料源發出即時請求' };
  return { status: snapshot.status || 'partial', generated_at: snapshot.generated_at,
    coverage: snapshot.coverage || null, rows: adaptSnapshotRows(snapshot) };
}
