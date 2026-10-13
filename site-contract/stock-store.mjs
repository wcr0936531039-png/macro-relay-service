import {normalizeTicker} from './stock-source.mjs';
// KV-compatible storage contract; preserves last-known-good data on provider failure.
export function snapshotKey(ticker){return 'stock_snapshot_v2:'+normalizeTicker(ticker);}
export async function saveStockSnapshot(kv,{ticker,observations,as_of=new Date().toISOString()}) {
  ticker=normalizeTicker(ticker);
  if(!kv||typeof kv.put!=='function') throw new Error('KV_UNAVAILABLE');
  if(!Array.isArray(observations)||!observations.every(o=>o.ticker===ticker&&o.status==='ok'&&o.source&&o.observed_at)) throw new Error('INVALID_OBSERVATIONS');
  if(observations.length===0) return {written:false,reason:'NO_VALID_OBSERVATIONS'};
  const key=snapshotKey(ticker);
  const previous=await loadStockSnapshot(kv,ticker);
  const byMetricDate=new Map();
  for(const o of [...(previous?.observations??[]),...observations]) byMetricDate.set(o.metric+'|'+o.observed_at,o);
  const snapshot={schema_version:2,ticker,updated_at:as_of,observations:[...byMetricDate.values()].sort((a,b)=>a.observed_at.localeCompare(b.observed_at))};
  await kv.put(key,JSON.stringify(snapshot));
  return {written:true,count:snapshot.observations.length,key};
}
export async function loadStockSnapshot(kv,ticker){
  ticker=normalizeTicker(ticker);
  if(!kv||typeof kv.get!=='function') throw new Error('KV_UNAVAILABLE');
  const raw=await kv.get(snapshotKey(ticker));
  if(raw===null||raw===undefined) return null;
  let value;try{value=typeof raw==='string'?JSON.parse(raw):raw;}catch{throw new Error('CORRUPT_SNAPSHOT');}
  if(value?.schema_version!==2||value.ticker!==ticker||!Array.isArray(value.observations)) throw new Error('CORRUPT_SNAPSHOT');
  return value;
}
export async function refreshStockSnapshot({kv,ticker,provider,as_of}){
  ticker=normalizeTicker(ticker);
  try {
    const observations=await provider(ticker);
    const result=await saveStockSnapshot(kv,{ticker,observations,as_of});
    return {status:result.written?'ok':'missing',...result};
  } catch(error){
    const prior=await loadStockSnapshot(kv,ticker);
    if(prior) return {status:'stale',reason:String(error?.message??error),snapshot:prior};
    return {status:'unavailable',reason:String(error?.message??error)};
  }
}
