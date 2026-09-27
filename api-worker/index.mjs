import { adaptSnapshotRows, validateSnapshot } from '../worker/read_macro_snapshot.js';

// Private server-to-server endpoint. Never embed SNAPSHOT_READ_TOKEN in browser code.
const AGE_DAYS = { SOFR:7, RRPONTSYD:7, RPONTSYD:7, PAYEMS:100, UNRATE:100,
  SAHMREALTIME:120, RETAIL_SALES_MOM:75, T10Y2Y:7, DFII10:7, T5YIE:7,
  TW_EXPORT_ORDERS:75, TW_NDC_SIGNAL:120, TPEX_BREADTH:5 };
const json = (body, status=200) => new Response(JSON.stringify(body), {
  status, headers: {'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff'}
});

export async function handle(request, env, now=Date.now()) {
  if (new URL(request.url).pathname !== '/api/market-snapshot') return json({error:'NOT_FOUND'},404);
  if (request.method !== 'GET') return new Response(null,{status:405,headers:{Allow:'GET'}});
  if (!env?.SNAPSHOT_READ_TOKEN || !env?.MACRO_KV?.get) return json({error:'NOT_CONFIGURED'},503);
  if (request.headers.get('Authorization') !== `Bearer ${env.SNAPSHOT_READ_TOKEN}`) return json({error:'UNAUTHORIZED'},401);
  try {
    const snapshot = await env.MACRO_KV.get('market_snapshot','json');
    if (!snapshot) return json({status:'uninitialized',error:'SNAPSHOT_NOT_INITIALIZED'},503);
    validateSnapshot(snapshot);
    const generated = Date.parse(snapshot.generated_at);
    const expired = !Number.isFinite(generated) || generated > now+60000 || now-generated > 36*3600000;
    const rows = adaptSnapshotRows(snapshot).map(row => {
      const observed = Date.parse(`${row.date}T00:00:00Z`);
      if (!Number.isFinite(observed) || observed > now+86400000) return {...row,value:null,status:'missing',reason:'觀測日期無效'};
      if (expired || now-observed > (AGE_DAYS[row.id]||30)*86400000) {
        return {...row,status:'stale',is_stale:true,reason:row.reason || (expired?'排程快照超過 36 小時未更新':'觀測期已超過時效門檻')};
      }
      return row;
    });
    const present = new Set(rows.map(row=>row.id));
    for (const id of Object.keys(AGE_DAYS)) {
      if (!present.has(id)) rows.push({id,value:null,date:null,status:'missing',is_stale:false,reason:'快照尚無有效觀測值'});
    }
    const usable = rows.filter(row=>row.status==='ok' && !row.is_stale && Number.isFinite(row.value)).length;
    const retained = rows.filter(row=>Number.isFinite(row.value)).length;
    return json({schema_version:1,status:usable===rows.length?'complete':'partial',generated_at:snapshot.generated_at,
      coverage:{usable,retained,total:rows.length},rows});
  } catch {
    // Do not disclose tokens or provider exception bodies to clients.
    return json({error:'SNAPSHOT_UNAVAILABLE',status:'unavailable'},503);
  }
}
export default {fetch(request, env) { return handle(request, env); }};
