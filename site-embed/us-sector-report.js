import {evaluateSectorSnapshot} from './us-sector-snapshot.js';
/** Optional upstream context: never changes the existing Macro Gate or VETO. */
export function buildSectorReport(snapshot = {}) {
  const evaluation=evaluateSectorSnapshot(snapshot);
  const observedAt=evaluation.benchmarkObservedAt;
  const coverage=evaluation.coverage;
  return {
    module:'US_SECTOR_ROTATION_V1',
    status:evaluation.status,
    classification:evaluation.classification,
    coverage:{valid:coverage,total:evaluation.total},
    benchmark:'SPY',
    observedAt:observedAt || null,
    generatedAt:evaluation.generatedAt,
    source:evaluation.source,
    sectors:evaluation.sectors,
    macroGateOverride:null,
    vetoOverride:null,
    scoreContribution:0,
    warnings:evaluation.status==='OK'?[]:['DATA_INCOMPLETE','NO_TRADING_DECISION']
  };
}
