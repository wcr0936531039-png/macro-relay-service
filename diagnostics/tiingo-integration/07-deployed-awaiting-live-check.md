# Deployment checkpoint — 2026-10-21 01:54 Taipei

The exact owner-approved patch was reapplied to clean baseline and full `npm test` exited 0. Rebuilt HTML and Worker hashes exactly match the reviewed artifacts. Source pushed as f9c5f15b371de58d0a06ef5251ce5c8a895f217e. Sites reports production deployment succeeded, new saved version **230** (v229-local integration). Owner-only audience unchanged.

Four pre-deployment Master reports captured privately. First live private Tiingo refresh now in progress. No raw Tiingo prices or service credentials are written to this repository. Additional local fault injection: 401 and 429 stop fan-out after one call and return Yahoo with 備援來源; empty data returns Yahoo after 22 attempts. These are simulated failures, not claims of real provider errors.

Pending: live dates/coverage/provider comparison/quota; four Master score and Gate comparison. Rollback target remains prior production v229 if site fails.
