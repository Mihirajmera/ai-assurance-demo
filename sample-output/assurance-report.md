# AI assurance report: Acme Release Agent

Review date 2026-10-12. One agent, assessed at three layers by three tools. **31 NIST SP 800-53 controls** have evidence, **8** of them from more than one layer; **13** are not satisfied.

| Layer | Question | Tool | Report |
|---|---|---|---|
| access | What is the agent allowed to do? | `agent-access-review` | [access-review.md](access/access-review.md) |
| runtime | What did it actually do? | `multiagent-flight-recorder` | [flight-report.md](runtime/flight-report.md) |
| gateway | Is the path its model calls take controlled? | `ai-gateway-audit` | [gateway-audit.md](gateway/gateway-audit.md) |

## Controls across layers

Each cell is that layer's result for the control and the checks behind it. A control is satisfied overall only when every layer that tested it passes.

| NIST 800-53 | Configuration | Runtime | Gateway | Overall |
|---|---|---|---|---|
| AC-2 | **FAIL** (AAR-01, AAR-02) |  | pass (GWA-05) | **FAIL** |
| AC-2(3) | **FAIL** (AAR-08) |  |  | **FAIL** |
| AC-3 |  | pass (AFR-03, AFR-05) | pass (GWA-02) | pass |
| AC-4 | **FAIL** (AAR-09) |  |  | **FAIL** |
| AC-5 |  | **FAIL** (AFR-04) |  | **FAIL** |
| AC-6 | **FAIL** (AAR-03, AAR-04, AAR-05) | pass (AFR-03) |  | **FAIL** |
| AU-3 |  | pass (AFR-02) |  | pass |
| AU-3(3) |  |  | pass (GWA-03) | pass |
| AU-9 |  | pass (AFR-01) |  | pass |
| AU-9(3) |  | pass (AFR-01) |  | pass |
| AU-10 |  | pass (AFR-01) |  | pass |
| AU-12 |  | pass (AFR-07) |  | pass |
| CM-2 |  |  | **FAIL** (GWA-07) | **FAIL** |
| CM-3 |  | **FAIL** (AFR-06) |  | **FAIL** |
| CM-7 | pass (AAR-05) |  | pass (GWA-09, GWA-10) | pass |
| CM-8 | pass (AAR-12) |  |  | pass |
| IA-2 |  |  | pass (GWA-02, GWA-05) | pass |
| IA-5 | **FAIL** (AAR-06, AAR-07) |  |  | **FAIL** |
| IA-5(7) |  |  | pass (GWA-01, GWA-02) | pass |
| RA-5 | pass (AAR-14) |  | pass (GWA-11) | pass |
| SA-22 | **FAIL** (AAR-13) |  |  | **FAIL** |
| SC-5 |  |  | pass (GWA-10) | pass |
| SC-6 |  |  | **FAIL** (GWA-06) | **FAIL** |
| SC-8 | pass (AAR-11) |  | pass (GWA-08) | pass |
| SC-12 |  |  | pass (GWA-04) | pass |
| SC-23 |  |  | pass (GWA-08) | pass |
| SC-28 |  |  | pass (GWA-01, GWA-04) | pass |
| SI-2 | **FAIL** (AAR-13, AAR-14) |  | pass (GWA-11) | **FAIL** |
| SI-7 |  | **FAIL** (AFR-06) | **FAIL** (GWA-07) | **FAIL** |
| SI-12 |  |  | pass (GWA-03) | pass |
| SR-3 | **FAIL** (AAR-10) |  |  | **FAIL** |

The merged OSCAL assessment results are in [`oscal/assessment-results.json`](oscal/assessment-results.json): one result per layer, with every evidence link pointing at the hashed file it came from. [`manifest.sha256`](manifest.sha256) hashes every file in this bundle.
