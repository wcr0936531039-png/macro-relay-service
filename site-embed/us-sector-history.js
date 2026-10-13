export function returnsFromCloses(rows) {
  if (!Array.isArray(rows)) return {status:'UNKNOWN'};
  const valid=rows.filter(x=>x && typeof x.date==='string' && Number.isFinite(x.close) && x.close>0).sort((a,b)=>a.date.localeCompare(b.date));
  const unique=[...new Map(valid.map(x=>[x.date,x])).values()];
  if(unique.length<21)return {status:'UNKNOWN',available:unique.length};
  const latest=unique[unique.length-1];
  const result={status:'OK',observedAt:latest.date};
  for(const n of [5,10,20])result['return'+n+'d']=(latest.close/unique[unique.length-1-n].close-1)*100;
  return result;
}
