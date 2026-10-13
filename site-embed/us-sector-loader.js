import {buildSectorReport} from './us-sector-report.js';
/** Read-only adapter for the existing site's analysis backend; no DOM mutation. */
export async function loadUSSectorReport(fetchImpl = fetch, url = 'https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/us_sector_history.json', now = new Date()) {
  try {
    const response=await fetchImpl(url,{cache:'no-store',signal:AbortSignal.timeout(8000)});
    if (!response.ok) throw new Error('HTTP_'+response.status);
    const data=await response.json();
    if (data.schema_version!==1 || !data.histories || !data.status) throw new Error('SCHEMA_MISMATCH');
    const report=buildSectorReport(data);
    const observed=report.observedAt;
    if (!observed || !/^\d{4}-\d{2}-\d{2}$/.test(observed)) throw new Error('INVALID_OBSERVED_DATE');
    const date=new Date(observed+'T00:00:00Z');
    const current=now instanceof Date?now:new Date(now);
    if (!Number.isFinite(date.getTime()) || !Number.isFinite(current.getTime()) || date.toISOString().slice(0,10)!==observed) throw new Error('INVALID_OBSERVED_DATE');
    const ageDays=(Date.UTC(current.getUTCFullYear(),current.getUTCMonth(),current.getUTCDate())-date.getTime())/86400000;
    if (ageDays<0 || ageDays>5) return {...buildSectorReport(),status:'UNKNOWN',errorCode:'STALE_DATA',warnings:['STALE_DATA','NO_TRADING_DECISION'],observedAt:observed};
    if (report.status!=='OK') return {...report,errorCode:'DATA_INCOMPLETE'};
    return report;
  } catch (error) {
    return {...buildSectorReport(),errorCode:'DATA_UNAVAILABLE'};
  }
}
