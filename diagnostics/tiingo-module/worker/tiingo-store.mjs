/** Shared D1 storage; rolling request limits are reserved by ONE atomic SQL UPDATE. */
export const GUARD_SCHEMA="CREATE TABLE IF NOT EXISTS tiingo_private_guard (id INTEGER PRIMARY KEY CHECK(id=1), requests TEXT NOT NULL DEFAULT '[]', symbols TEXT NOT NULL DEFAULT '{}', month TEXT NOT NULL DEFAULT '', lease_owner TEXT, lease_until INTEGER NOT NULL DEFAULT 0)";
export const RESERVE_SQL=`UPDATE tiingo_private_guard SET
 requests=json_insert(COALESCE((SELECT json_group_array(json(value)) FROM json_each(requests) WHERE json_extract(value,'$.at')>?), '[]'),'$[#]',json(?)),
 symbols=CASE WHEN month=? THEN json_set(symbols,?,1) ELSE json_object(?,1) END, month=?
 WHERE id=1 AND (SELECT count(*) FROM json_each(requests) WHERE json_extract(value,'$.at')>?)<50
 AND (SELECT count(*) FROM json_each(requests) WHERE json_extract(value,'$.at')>?)<1000
 AND (month<>? OR json_type(symbols,?) IS NOT NULL OR (SELECT count(*) FROM json_each(symbols))<500)
 RETURNING id`;
export const LEASE_SQL='UPDATE tiingo_private_guard SET lease_owner=?,lease_until=? WHERE id=1 AND lease_until<=? RETURNING id';
export async function createPrivateStore({db,read,write}){
  if(!db?.prepare||!read||!write)throw Error('PRIVATE_STORAGE_UNAVAILABLE');
  await db.prepare(GUARD_SCHEMA).run();
  await db.prepare('INSERT OR IGNORE INTO tiingo_private_guard (id) VALUES (1)').run();
  const change=async(sql,args)=>(await db.prepare(sql).bind(...args).all())?.results?.length>0;
  return {
    cache:{get:async key=>(await read(key))?.payload||null,set:async(key,value)=>write(key,value,370*86400000)},
    quota:{reserve:async(symbol,now)=>{
      if(!/^[A-Z]{1,8}$/.test(symbol)||!Number.isFinite(now))return false;
      const month=new Date(now).toISOString().slice(0,7),path=`$.${symbol}`;
      return change(RESERVE_SQL,[now-86400000,JSON.stringify({at:now,symbol}),month,path,symbol,month,now-3600000,now-86400000,month,path]);
    }},
    acquire:(owner,now)=>change(LEASE_SQL,[owner,now+15*60000,now]),
    release:async owner=>db.prepare('UPDATE tiingo_private_guard SET lease_until=0,lease_owner=NULL WHERE id=1 AND lease_owner=?').bind(owner).run()
  };
}
