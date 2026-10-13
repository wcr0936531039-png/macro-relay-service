/** Cross-market divergence gate. Pure logic, no DOM changes. */
export function evaluateCrossMarket(input = {}) {
  const finite = x => typeof x === 'number' && Number.isFinite(x);
  const required = ['twReturn5d','usReturn5d','twReturn10d','usReturn10d','breadthRatio','foreignNetTwd','nonDayTradeTrend'];
  const missing = required.filter(k => !finite(input[k]));
  const relative5d = finite(input.twReturn5d) && finite(input.usReturn5d) ? input.twReturn5d - input.usReturn5d : null;
  const relative10d = finite(input.twReturn10d) && finite(input.usReturn10d) ? input.twReturn10d - input.usReturn10d : null;
  const evidence = {relative5d, relative10d, breadthRatio: input.breadthRatio ?? null, foreignNetTwd: input.foreignNetTwd ?? null, nonDayTradeTrend: input.nonDayTradeTrend ?? null, earningsRevision: input.earningsRevision ?? null, creditStress: input.creditStress ?? null};
  if (missing.length) return {status:'UNKNOWN', classification:'DATA_INCOMPLETE', missing, evidence, veto:false};
  const divergent = relative5d > 0 && relative10d > 0 && input.usReturn5d < 0;
  if (!divergent) return {status:'NEUTRAL', classification:'NO_CONFIRMED_DIVERGENCE', missing:[], evidence, veto:false};
  const broad = input.breadthRatio > 1;
  const funded = input.foreignNetTwd >= 0 || input.nonDayTradeTrend > 0;
  const earningsConfirmed = finite(input.earningsRevision) && input.earningsRevision > 0;
  const creditKnown = typeof input.creditStress === 'boolean';
  if (!creditKnown || !finite(input.earningsRevision)) return {status:'UNKNOWN', classification:'DIVERGENCE_UNDER_REVIEW', missing:[...(!creditKnown?['creditStress']:[]),...(!finite(input.earningsRevision)?['earningsRevision']:[])], evidence, veto:false};
  if (broad && funded && earningsConfirmed && !input.creditStress) return {status:'GREEN', classification:'FUNDAMENTAL_DIVERGENCE', missing:[], evidence, veto:false};
  if (!broad && !funded && input.creditStress) return {status:'RED', classification:'FRAGILE_DIVERGENCE', missing:[], evidence, veto:false};
  return {status:'YELLOW', classification:'STRUCTURAL_DIVERGENCE', missing:[], evidence, veto:false};
}
