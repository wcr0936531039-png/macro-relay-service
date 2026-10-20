import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {SECTORS,GLOBAL,SYMBOLS,fetchTiingoDaily,selectSession,breadth,refreshPrivateMarket} from '../worker/tiingo-market.mjs';
import {GUARD_SCHEMA,RESERVE_SQL,LEASE_SQL} from '../worker/tiingo-store.mjs';
const now=new Date('2026-10-20T12:00:00Z'),expectedSession='2026-10-19';
const history=Array.from({length:270},(_,i)=>({date:new Date(Date.parse(expectedSession)-(269-i)*86400000).toISOString().slice(0,10),price:100+i}));
const item=(symbol,h=history)=>({status:'ok',symbol,priceField:'adjClose',observedAt:h.at(-1).date,history:h});
const snapshots=()=>Object.fromEntries(SYMBOLS.map(s=>[s,item(s)]));

test('exact 22 tickers; ten markets, one vote each',()=>{assert.equal(SYMBOLS.length,22);assert.equal(SECTORS.length,11);assert.deepEqual(GLOBAL,['SPY','EWJ','MCHI','EWU','EWC','INDA','EWT','EWG','EWQ','EWY']);});
test('exclude later-than-expected bars before observedAt; auth header only, adjClose only',async()=>{
  let call;const response=[{date:'2026-10-16',adjClose:101,close:1},{date:'2026-10-19',adjClose:102,close:2},{date:'2026-10-20',adjClose:9999,close:3}];
  const r=await fetchTiingoDaily('SPY',{token:'synthetic-test-credential',expectedSession,now,fetchImpl:async(u,o)=>{call={u,o};return Response.json(response);}});
  assert.equal(r.observedAt,expectedSession);assert.equal(r.history.at(-1).price,102);assert.equal(r.excludedFutureRows,1);assert.equal(selectSession(r,expectedSession).status,'ok');
  assert.equal(call.o.headers.Authorization,'Token synthetic-test-credential');assert.ok(!call.u.includes('synthetic-test-credential'));assert.ok(!JSON.stringify(r).includes('credential'));
});
test('defensive stored-result filtering and missing completed session retain original last-good',()=>{
  const old=item('SPY',history.slice(0,-1)),future={...item('SPY'),history:[...history,{date:'2026-10-20',price:999}]};
  assert.equal(selectSession(future,expectedSession,old).observedAt,expectedSession);
  const failed=selectSession(old,expectedSession,old);assert.equal(failed.status,'source_failed');assert.equal(failed.previous.observedAt,'2026-10-18');
});
test('401/403/429/empty/invalid JSON/exception are sanitized',async()=>{
  for(const status of [401,403,429,503]){const r=await fetchTiingoDaily('SPY',{token:'test-secret',expectedSession,now,fetchImpl:async()=>new Response('test-secret',{status})});assert.equal(r.status,'source_failed');assert.ok(!JSON.stringify(r).includes('test-secret'));}
  for(const fetchImpl of [async()=>Response.json([]),async()=>new Response('broken'),async()=>{throw Error('test-secret');}])assert.equal((await fetchTiingoDaily('SPY',{token:'test-secret',expectedSession,now,fetchImpl})).status,'source_failed');
});
test('conflicting duplicates are rejected, not overwritten',async()=>{const r=await fetchTiingoDaily('SPY',{token:'test',expectedSession,now,fetchImpl:async()=>Response.json([{date:expectedSession,adjClose:1},{date:expectedSession,adjClose:2}])});assert.equal(r.code,'conflicting_duplicate');});
test('200 samples required; partial global breadth uses observed denominator only, SPY mandatory',()=>{
  const data=snapshots();data.EWJ=item('EWJ',history.slice(-199));let b=breadth(data);assert.equal(b.globalBreadth.coverage,9);assert.equal(b.globalBreadth.denominator,9);assert.equal(b.globalBreadth.ratio,1);assert.equal(b.globalBreadth.complete,false);
  data.SPY={status:'source_failed'};b=breadth(data);assert.equal(b.globalBreadth.ratio,null);assert.equal(b.globalBreadth.denominator,null);
  data.XLK=item('XLK',history.slice(-199));assert.equal(breadth(data).sectorBreadth.coverage,10);
});
test('RSP/SPY is exactly 20 aligned sessions, not intersection extended across a hole',()=>{const data=snapshots();assert.equal(breadth(data).equalWeightRatio20d,0);data.RSP.history=data.RSP.history.filter((_,i)=>i!==260);assert.equal(breadth(data).equalWeightRatio20d,null);});
test('persistent same-session cache survives a fresh refresh invocation without quota/fetch',async()=>{
  const map=new Map(Object.entries(snapshots()).map(([s,x])=>[`tiingo:${s}`,x]));let calls=0;
  const cache={get:async k=>map.get(k),set:async(k,x)=>{map.set(k,x);return true;}},quota={reserve:async()=>{calls++;return true;}};
  const r=await refreshPrivateMarket({token:'test',expectedSession,now,cache,quota,fetchImpl:async()=>{throw Error('should not fetch');}});assert.equal(r.requestCount,0);assert.equal(calls,0);
});
test('429 stops the fan-out, persists cooldown; next invocation makes zero requests',async()=>{
  const map=new Map(),cache={get:async k=>map.get(k),set:async(k,x)=>{map.set(k,x);return true;}},quota={reserve:async()=>true};let calls=0;
  const args={token:'test',expectedSession,now,cache,quota,fetchImpl:async()=>{calls++;return new Response('',{status:429});}};
  await refreshPrivateMarket(args);await refreshPrivateMarket(args);assert.equal(calls,1);assert.equal(map.size,22);
});
test('without persistent cache and atomic reservation no network call is allowed',async()=>{await assert.rejects(refreshPrivateMarket({token:'test',expectedSession,now,cache:{get(){},set(){}},quota:{canFetch(){},record(){}}}),/ATOMIC_QUOTA/);});
test('actual SQLite: concurrent reservations cap at 50, rolling-hour boundary, day/month guards and single refresh lease',()=>{
  const code=`import json,sqlite3,tempfile,concurrent.futures,sys,os
d=json.load(sys.stdin);tmp=tempfile.TemporaryDirectory();path=os.path.join(tmp.name,'quota.db');now=1792497600000
def conn():
 c=sqlite3.connect(path,timeout=30);c.execute('PRAGMA journal_mode=WAL');return c
c=conn();c.execute(d['schema']);c.execute('INSERT INTO tiingo_private_guard (id) VALUES (1)');c.commit();c.close()
def reserve(i,t=now):
 c=conn();sym='SPY';month='2026-10';p='$.SPY';args=[t-86400000,json.dumps({'at':t,'symbol':sym}),month,p,sym,month,t-3600000,t-86400000,month,p]
 r=c.execute(d['reserve'],args).fetchall();c.commit();c.close();return bool(r)
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex: results=list(ex.map(reserve,range(100)))
assert sum(results)==50,sum(results)
assert not reserve(0,now+3599999)
assert reserve(0,now+3600001)
c=conn();c.execute('UPDATE tiingo_private_guard SET requests=?',(json.dumps([{'at':now-4000000,'symbol':'SPY'}]*1000),));c.commit();assert not reserve(0)
c.execute('UPDATE tiingo_private_guard SET requests=?, symbols=?, month=?',('[]',json.dumps({str(i):1 for i in range(500)}),'2026-10'));c.commit();assert not reserve(0)
c.execute('UPDATE tiingo_private_guard SET symbols=?',('{}',));c.commit()
def lease(i):
 c=conn();r=c.execute(d['lease'],[str(i),now+900000,now]).fetchall();c.commit();c.close();return bool(r)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: assert sum(ex.map(lease,range(32)))==1
print('SQL concurrency and all limits passed')`;
  const r=spawnSync('python',['-c',code],{input:JSON.stringify({schema:GUARD_SCHEMA,reserve:RESERVE_SQL,lease:LEASE_SQL}),encoding:'utf8'});assert.equal(r.status,0,r.stderr);
});
