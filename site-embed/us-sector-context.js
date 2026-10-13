import {loadUSSectorReport} from './us-sector-loader.js';

/** Attach optional, read-only US sector context to an existing Master Model report.
 * Never mutates the original report, Macro Gate, 10D, VETO or score.
 */
export async function attachUSSectorContext(report, fetchImpl=fetch, now=new Date()) {
  if (!report || typeof report!=='object' || Array.isArray(report)) throw new TypeError('REPORT_REQUIRED');
  const sector=await loadUSSectorReport(fetchImpl,undefined,now);
  return {...report,usSectorContext:{
    module:sector.module,
    status:sector.status,
    errorCode:sector.errorCode || null,
    classification:sector.classification,
    coverage:sector.coverage,
    benchmark:sector.benchmark,
    observedAt:sector.observedAt,
    generatedAt:sector.generatedAt,
    source:sector.source,
    sectors:sector.sectors,
    warnings:sector.warnings,
    scoreContribution:0,
    macroGateOverride:null,
    vetoOverride:null
  }};
}
