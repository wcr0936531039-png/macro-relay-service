import {createReport,updateModule,evaluateReport} from './report-state.mjs';
import {normalizeTicker,normalizeObservation,sourceCoverage} from './stock-source.mjs';

// Deterministic assembly only. Providers/AI operate outside this module.
export function assembleStockReport({ticker,observations=[],requiredMetrics=['revenue','eps'],macroEvidence=[],researchEvidence=[],screeningEvidence=[],valuationEvidence=[],vetoEvidence=[],rating=null}) {
  ticker=normalizeTicker(ticker);
  const normalized=observations.map(normalizeObservation);
  const coverage=sourceCoverage(normalized,ticker,requiredMetrics);
  const scoped=normalized.filter(x=>x.ticker===ticker);
  let report=createReport(ticker);
  const evidence=scoped.filter(x=>x.status==='ok');
  report=updateModule(report,'fundamentals',{status:coverage.status,evidence});
  for (const [key,rows] of Object.entries({macro:macroEvidence,research:researchEvidence,screening:screeningEvidence,valuation:valuationEvidence,veto:vetoEvidence})) {
    if (!Array.isArray(rows)) throw new Error('INVALID_EVIDENCE');
    const status=rows.length?'partial':key==='veto'?'unknown':'pending';
    report=updateModule(report,key,{status,evidence:rows});
  }
  report.coverage=coverage;
  report.observations=scoped;
  // No automatic final rating: modules require independent verification.
  return evaluateReport(report,{rating});
}
