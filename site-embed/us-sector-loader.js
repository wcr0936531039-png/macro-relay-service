import {buildSectorReport} from './us-sector-report.js';
/** Read-only adapter for the existing site's analysis backend; no DOM mutation. */
export async function loadUSSectorReport(fetchImpl = fetch, url = 'https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/us_sector_history.json') {
  try {
    const response=await fetchImpl(url,{cache:'no-store'});
    if (!response.ok) throw new Error('HTTP_'+response.status);
    const data=await response.json();
    if (data.schema_version!==1 || !data.histories || !data.status) throw new Error('SCHEMA_MISMATCH');
    return buildSectorReport(data);
  } catch (error) {
    return {...buildSectorReport(),errorCode:'DATA_UNAVAILABLE'};
  }
}
