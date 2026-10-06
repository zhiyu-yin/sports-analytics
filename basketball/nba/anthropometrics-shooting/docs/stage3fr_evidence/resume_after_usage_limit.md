# Resume after usage limit

The user reports that the prior Stage 3F-R interaction was interrupted by Codex usage exhaustion. This was an infrastructure/session interruption only and did not trigger any scientific gate.

On resume, the existing diagnostic orchestrator remained alive. DIAG-A attempt 1 had completed with a valid saved trace and diagnostics. Its frozen numerical gate failed, so the existing process had already begun its single predeclared recovery. That recovery was triggered by sampler diagnostics, not by the session interruption. No computation was restarted on resume.

Reused completed artifacts: predictor design audit, fixed-effect conditioning audit, both failed-F2 convergence/geometry audits, frozen reparameterization protocol and R3 derivation, R1 equivalence validation and paired original prior draws, and DIAG-A attempt 1. Protocol/model/decomposition hashes, R1 validation model hashes, and the completed DIAG-A trace hash were verified on resume. R1 equivalence checks were not repeated.

No model, prior, data, threshold, draw budget, or scientific rule changed. The scientific-effect firewall remains active. The existing process continues DIAG-A recovery, then DIAG-B and DIAG-C under the frozen plan.
